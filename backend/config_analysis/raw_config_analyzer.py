"""
Raw Configuration Analyzer.

Analyses plain-text configuration files (shell scripts, firewall loaders,
nginx/system conf files, log files, etc.) that cannot be parsed as structured
data formats.

Entry point: analyze_raw_config(raw_text, filename, framework)
Returns a structured analysis dict consumed by process_config_upload.
"""

import re
from typing import Any


# ---------------------------------------------------------------------------
# Comment stripping — run BEFORE extraction to eliminate noise
# ---------------------------------------------------------------------------

def _strip_comments(text: str) -> str:
    """Return *code-only* text with full-line and inline comments removed.

    - Lines starting with ``#`` (after optional whitespace) are dropped entirely
      EXCEPT shebang lines (``#!/…``) which carry semantic value.
    - Inline comments (``command  # comment``) have the trailing part stripped.
    """
    cleaned: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        # Keep shebang
        if stripped.startswith("#!"):
            cleaned.append(line)
            continue
        # Drop full-line comments
        if stripped.startswith("#"):
            continue
        # Strip inline comments (simple heuristic: space-hash not inside quotes)
        code_part = re.sub(r"\s+#(?!!).*$", "", line)
        cleaned.append(code_part)
    return "\n".join(cleaned)


# ---------------------------------------------------------------------------
# Config-type detection
# ---------------------------------------------------------------------------

_TYPE_PATTERNS: list[tuple[str, list[str]]] = [
    ("firewall", [
        r"\biptables\b", r"\bnft\b", r"\bfirewall-cmd\b",
        r"\bpf\.conf\b", r"INPUT|OUTPUT|FORWARD",
        r"\bDROP\b", r"\bACCEPT\b", r"\bREJECT\b",
        r"--dport", r"-A\s+\w+",
    ]),
    ("nginx", [
        r"\bserver\s*\{", r"\blocation\s+[/\w]", r"\blisten\s+\d+",
        r"\bproxy_pass\b", r"\broot\s+/", r"\bssl_certificate\b",
    ]),
    ("system", [
        r"\[Unit\]", r"\[Service\]", r"\[Install\]",      # systemd
        r"^\s*\w+=\S+",                                   # sysconfig style
        r"\bCHROOT\b", r"\bPAM\b", r"\bsshd_config\b",
    ]),
    ("shell_script", [
        r"^#!/", r"\bexport\b", r"\bsource\b", r"\. /",
        r"\bfunction\b", r"\bfi\b", r"\bdo\b", r"\bdone\b",
    ]),
    ("log_file", [
        r"\b(ERROR|WARN|INFO|DEBUG|CRITICAL)\b",
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",          # ISO timestamp
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d",
    ]),
]


def _detect_config_type(text: str) -> str:
    """Return the best-match config type label for the raw text.

    Special sub-type: a shell script that loads ``*.fw`` glob files is tagged
    as ``firewall_loader`` so findings can be more specific.
    """
    code = _strip_comments(text)
    counts: dict[str, int] = {}
    for config_type, patterns in _TYPE_PATTERNS:
        score = sum(
            1 for p in patterns if re.search(p, code, re.MULTILINE | re.IGNORECASE)
        )
        if score:
            counts[config_type] = score
    if not counts:
        return "generic"

    best = max(counts, key=lambda k: counts[k])

    # Promote to firewall_loader when a shell/firewall script loads *.fw files
    if best in ("shell_script", "firewall") and re.search(r"\*\.fw\b", code):
        return "firewall_loader"
    return best


# ---------------------------------------------------------------------------
# Component extraction helpers
# ---------------------------------------------------------------------------

def _extract_components(text: str, config_type: str) -> list[dict]:
    """Extract meaningful components from the **code-only** text.

    Comments are stripped first so we never surface values like
    ``SOURCED_FILE:#NOTE`` that originate in comment lines.
    """
    code = _strip_comments(text)
    components: list[dict] = []
    _seen_values: set[str] = set()  # quick dedup guard

    def _add(comp_type: str, value: str) -> None:
        value = value.strip().rstrip("/")
        if not value or value in _seen_values:
            return
        _seen_values.add(value)
        components.append({"type": comp_type, "value": value})

    # -- Firewall / firewall_loader specifics --
    if config_type in ("firewall", "firewall_loader"):
        # iptables-style rules
        for m in re.finditer(r"iptables\s+(.+)", code):
            _add("iptables_rule", m.group(0))
        # nftables-style
        for m in re.finditer(r"nft\s+(.+)", code):
            _add("nftables_rule", m.group(0))
        # Glob execution patterns (e.g. *.fw, *.conf)
        for m in re.finditer(r"(\*\.\w+)", code):
            _add("execution_pattern", m.group(1))
        # Directories used in loops or run-parts
        for m in re.finditer(r"(?:run-parts|in)\s+(/[\w./-]+)", code):
            _add("file_path", m.group(1))
        # Loop-based execution
        if re.search(r"for\s+\w+\s+in\s+", code):
            _add("loop_execution", "yes")
        # Script sub-type
        if config_type == "firewall_loader":
            _add("script_type", "firewall_loader")

    # -- nginx --
    elif config_type == "nginx":
        for m in re.finditer(r"listen\s+([\d.:]+(?::\d+)?)", code):
            _add("listen_port", m.group(1))
        for m in re.finditer(r"server_name\s+([^;]+);", code):
            _add("server_name", m.group(1).strip())
        for m in re.finditer(r"ssl_certificate\s+([^;]+);", code):
            _add("ssl_cert_path", m.group(1).strip())

    # -- shell_script --
    elif config_type == "shell_script":
        # Source'd files (code-only — comments already gone)
        for m in re.finditer(r"(?:source|\.)\s+(/[\w./-]+)", code):
            _add("sourced_file", m.group(1))
        # Exported variables
        for m in re.finditer(r"export\s+([A-Z_][A-Z0-9_]*)", code):
            _add("exported_var", m.group(1))
        # Detect loops
        if re.search(r"for\s+\w+\s+in\s+", code):
            _add("loop_execution", "yes")

    # -- Generic: file paths referenced in code --
    for m in re.finditer(r"(/(?:etc|usr|var|opt|home|tmp)/[\w./-]+)", code):
        _add("file_path", m.group(1))

    return components


# ---------------------------------------------------------------------------
# Misconfiguration detectors
# ---------------------------------------------------------------------------

_Finding = dict[str, Any]

_SEVERITY_WEIGHTS = {"High": 3, "Medium": 2, "Low": 1}


def _check_firewall(text: str) -> list[_Finding]:
    """Firewall / firewall_loader findings — runs on comment-stripped code."""
    code = _strip_comments(text)
    findings: list[_Finding] = []

    # Execute-all-files-in-directory pattern (run-parts or glob loop)
    if re.search(r"run-parts\s+/|for\s+\w+\s+in\s+[/\w.*]+", code):
        findings.append({
            "id": "FW-001",
            "title": "Unrestricted Directory Execution",
            "description": (
                "All files in a directory are executed without validation. "
                "A compromised or injected file would be loaded as a firewall rule."
            ),
            "severity": "High",
            "category": "Integrity",
            "recommendation": "Enumerate allowed rule files explicitly; never use run-parts or glob loops on untrusted directories.",
        })

    # No validation of rules before execution
    if not re.search(r"iptables-restore\s+--test|iptables\s+--check|nft\s+-c", code):
        findings.append({
            "id": "FW-007",
            "title": "No Rule Validation Before Execution",
            "description": (
                "Firewall rules are applied without a dry-run or syntax check. "
                "A malformed rule could disrupt network connectivity."
            ),
            "severity": "High",
            "category": "Integrity",
            "recommendation": "Run 'iptables-restore --test' or 'nft -c' before applying rules to validate syntax.",
        })

    # No integrity check (no hash/checksum verification)
    if not re.search(r"(?:sha256sum|md5sum|gpg --verify|openssl dgst)", code):
        findings.append({
            "id": "FW-002",
            "title": "Missing Integrity Verification",
            "description": "No cryptographic integrity check is performed on loaded rule files.",
            "severity": "High",
            "category": "Integrity",
            "recommendation": "Verify file checksums (SHA-256 or GPG signatures) before execution.",
        })

    # Reliance on executable permission only (no ownership / attribute check)
    has_perm_check = re.search(r"\[\s+-[xXrRfF]|-x\s|\btest\b.*-[xX]", code)
    has_owner_check = re.search(r"stat\b|chown\b|\bowner\b", code, re.IGNORECASE)
    if has_perm_check and not has_owner_check:
        findings.append({
            "id": "FW-008",
            "title": "Execution Gated Only by Permission Bit",
            "description": (
                "Script checks the executable bit (-x) but does not verify file "
                "ownership. Any user who can set +x could inject rules."
            ),
            "severity": "Medium",
            "category": "Access Control",
            "recommendation": "Verify both file ownership (root:root) and restricted permissions (e.g. 0700) before execution.",
        })
    elif not has_perm_check:
        findings.append({
            "id": "FW-003",
            "title": "No Permission Validation Before Execution",
            "description": "Scripts are executed without checking ownership or execute-bit permissions.",
            "severity": "Medium",
            "category": "Access Control",
            "recommendation": "Verify that only root-owned files with restricted permissions are executed.",
        })

    # Default-allow pattern
    if re.search(r"-P\s+(INPUT|OUTPUT|FORWARD)\s+ACCEPT", code):
        findings.append({
            "id": "FW-004",
            "title": "Default-Allow Policy Detected",
            "description": "One or more chains use a default ACCEPT policy, permitting all unmatched traffic.",
            "severity": "High",
            "category": "Network Security",
            "recommendation": "Set default policies to DROP or REJECT and explicitly allow required traffic.",
        })

    # Potential unsafe rule injection via shell variables
    if re.search(r"\$\{?\w+\}?.*iptables|iptables.*\$\{?\w+\}?", code):
        findings.append({
            "id": "FW-005",
            "title": "Potential Rule Injection via Shell Variable",
            "description": "Firewall rules are constructed using unvalidated shell variables, enabling injection.",
            "severity": "High",
            "category": "Input Validation",
            "recommendation": "Sanitize and validate all variables before using them in iptables/nft commands.",
        })

    # Allow-all rule
    if re.search(r"-A\s+INPUT\s+-j\s+ACCEPT\s*$|--dport\s+0:65535", code, re.MULTILINE):
        findings.append({
            "id": "FW-006",
            "title": "Broad Allow-All Rule Present",
            "description": "A rule unconditionally accepts all inbound traffic, bypassing firewall controls.",
            "severity": "High",
            "category": "Network Security",
            "recommendation": "Remove or scope catch-all ACCEPT rules; apply least-privilege network policy.",
        })

    return findings


def _check_nginx(text: str) -> list[_Finding]:
    findings: list[_Finding] = []

    if not re.search(r"ssl_certificate\b", text):
        findings.append({
            "id": "NGX-001",
            "title": "No TLS Certificate Configured",
            "description": "No ssl_certificate directive was found; traffic may be served over plain HTTP.",
            "severity": "High",
            "category": "Encryption",
            "recommendation": "Configure ssl_certificate and ssl_certificate_key for all production servers.",
        })

    if re.search(r"ssl_protocols\s+.*SSLv[23]|TLSv1[^.]", text):
        findings.append({
            "id": "NGX-002",
            "title": "Weak/Deprecated TLS Protocol Enabled",
            "description": "SSLv2/3 or TLS 1.0/1.1 is explicitly enabled.",
            "severity": "High",
            "category": "Encryption",
            "recommendation": "Allow only TLSv1.2 and TLSv1.3.",
        })

    if not re.search(r"server_tokens\s+off", text):
        findings.append({
            "id": "NGX-003",
            "title": "Server Version Disclosure",
            "description": "server_tokens is not set to off; nginx version may be revealed to attackers.",
            "severity": "Low",
            "category": "Information Disclosure",
            "recommendation": "Add 'server_tokens off;' to the http block.",
        })

    return findings


def _check_shell_script(text: str) -> list[_Finding]:
    """Shell-script findings — runs on comment-stripped code."""
    code = _strip_comments(text)
    findings: list[_Finding] = []

    if not re.search(r"set\s+-[eEuU]|set\s+-o\s+(?:errexit|nounset)", code):
        findings.append({
            "id": "SH-001",
            "title": "Missing Strict Shell Mode",
            "description": "Script does not use 'set -euo pipefail'; errors may be silently ignored.",
            "severity": "Medium",
            "category": "Error Handling",
            "recommendation": "Add 'set -euo pipefail' at the top of the script.",
        })

    # World-writable path sourced
    if re.search(r"(?:source|\.)\s+/tmp/", code):
        findings.append({
            "id": "SH-002",
            "title": "Sourcing File from /tmp",
            "description": "A file in the world-writable /tmp directory is sourced, enabling code injection.",
            "severity": "High",
            "category": "Input Validation",
            "recommendation": "Never source files from /tmp or other world-writable directories.",
        })

    # Unquoted variables in critical commands
    if re.search(r"(?:rm|chmod|chown|sudo)\s+[^\"'][^\n]*\$\w+", code):
        findings.append({
            "id": "SH-003",
            "title": "Unquoted Variable in Privileged Command",
            "description": "Shell variables are used unquoted in privileged commands; word splitting may cause errors or exploitation.",
            "severity": "Medium",
            "category": "Input Validation",
            "recommendation": "Always double-quote variables: \"$variable\".",
        })

    return findings


def _check_generic(text: str) -> list[_Finding]:
    """Checks applicable to any config type — runs on comment-stripped code."""
    code = _strip_comments(text)
    findings: list[_Finding] = []

    if re.search(r"(?:password|secret|api[_-]?key|token)\s*=\s*\S+", code, re.IGNORECASE):
        findings.append({
            "id": "GEN-001",
            "title": "Plaintext Credential Detected",
            "description": "A password, secret, or API key appears to be stored in plaintext in the config file.",
            "severity": "High",
            "category": "Secrets Management",
            "recommendation": "Remove credentials from config files; use a secrets manager or environment variable injection.",
        })

    if re.search(r"chmod\s+777|chmod\s+-R\s+777", code):
        findings.append({
            "id": "GEN-002",
            "title": "World-Writable Permission Set",
            "description": "chmod 777 grants write access to all users, creating a privilege escalation path.",
            "severity": "High",
            "category": "Access Control",
            "recommendation": "Apply least-privilege permissions; avoid 777 on any production path.",
        })

    return findings


# ---------------------------------------------------------------------------
# Framework mapping
# ---------------------------------------------------------------------------

_FRAMEWORK_CONTROL_MAP: dict[str, dict[str, str]] = {
    "iso27001": {
        "Integrity":            "A.12.2 — Protection from malware",
        "Access Control":       "A.9.4 — System and application access control",
        "Network Security":     "A.13.1 — Network controls",
        "Encryption":           "A.10.1 — Policy on use of cryptographic controls",
        "Secrets Management":   "A.9.2 — User access management",
        "Information Disclosure": "A.18.1 — Compliance with legal and contractual requirements",
        "Error Handling":       "A.14.2 — Security in development and support processes",
        "Input Validation":     "A.14.2 — Security in development and support processes",
    },
    "pci_dss": {
        "Network Security":     "PCI-DSS Req 1 — Install and maintain a firewall",
        "Encryption":           "PCI-DSS Req 4 — Encrypt transmission of cardholder data",
        "Access Control":       "PCI-DSS Req 7 — Restrict access by business need-to-know",
        "Secrets Management":   "PCI-DSS Req 8 — Assign unique IDs and protect credentials",
        "Integrity":            "PCI-DSS Req 11 — Regularly test security systems",
        "Input Validation":     "PCI-DSS Req 6 — Develop and maintain secure systems",
        "Information Disclosure": "PCI-DSS Req 12 — Maintain an information security policy",
        "Error Handling":       "PCI-DSS Req 6 — Develop and maintain secure systems",
    },
    "hipaa": {
        "Access Control":       "HIPAA §164.312(a)(1) — Access Control",
        "Encryption":           "HIPAA §164.312(e)(2)(ii) — Encryption and Decryption",
        "Integrity":            "HIPAA §164.312(c)(1) — Integrity controls",
        "Network Security":     "HIPAA §164.312(e)(1) — Transmission Security",
        "Secrets Management":   "HIPAA §164.312(a)(2)(i) — Unique User Identification",
        "Information Disclosure": "HIPAA §164.308(a)(4) — Information Access Management",
        "Error Handling":       "HIPAA §164.308(a)(1) — Security Management Process",
        "Input Validation":     "HIPAA §164.308(a)(1) — Security Management Process",
    },
    "nist": {
        "Access Control":       "NIST SP 800-53 AC — Access Control",
        "Integrity":            "NIST SP 800-53 SI — System and Information Integrity",
        "Network Security":     "NIST SP 800-53 SC — System and Communications Protection",
        "Encryption":           "NIST SP 800-53 SC-28 — Protection of Information at Rest",
        "Secrets Management":   "NIST SP 800-53 IA — Identification and Authentication",
        "Information Disclosure": "NIST SP 800-53 RA — Risk Assessment",
        "Error Handling":       "NIST SP 800-53 SA — System and Services Acquisition",
        "Input Validation":     "NIST SP 800-53 SI-10 — Information Input Validation",
    },
}


def _map_to_framework(findings: list[_Finding], framework: str) -> list[dict]:
    """Add a framework_control field to each finding where a mapping exists."""
    fw_key = framework.lower().replace(" ", "_").replace("-", "_")
    control_map = _FRAMEWORK_CONTROL_MAP.get(fw_key, {})
    enriched = []
    for f in findings:
        item = dict(f)
        category = f.get("category", "")
        item["framework_control"] = control_map.get(category, "No direct mapping")
        enriched.append(item)
    return enriched


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def _build_summary(findings: list[_Finding], config_type: str) -> dict:
    by_severity: dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        sev = f.get("severity", "Low")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    total = len(findings)
    if by_severity["High"] > 0:
        overall_risk = "High"
    elif by_severity["Medium"] > 0:
        overall_risk = "Medium"
    elif total > 0:
        overall_risk = "Low"
    else:
        overall_risk = "Informational"

    return {
        "config_type": config_type,
        "total_findings": total,
        "high": by_severity["High"],
        "medium": by_severity["Medium"],
        "low": by_severity["Low"],
        "overall_risk": overall_risk,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyze_raw_config(raw_text: str, filename: str, framework: str = "iso27001") -> dict:
    """
    Analyse a raw text configuration file and return structured security findings.

    Parameters
    ----------
    raw_text : str
        The full text content of the uploaded config file.
    filename : str
        Original filename (used for extension hints).
    framework : str
        Compliance framework to map findings to (iso27001 / pci_dss / hipaa / nist).

    Returns
    -------
    dict
        {
            config_type, components, summary, findings, recommendations
        }
    """
    config_type = _detect_config_type(raw_text)
    components = _extract_components(raw_text, config_type)

    # Gather findings from type-specific + generic checkers
    findings: list[_Finding] = []
    if config_type in ("firewall", "firewall_loader"):
        findings.extend(_check_firewall(raw_text))
    elif config_type == "nginx":
        findings.extend(_check_nginx(raw_text))
    elif config_type == "shell_script":
        findings.extend(_check_shell_script(raw_text))

    findings.extend(_check_generic(raw_text))

    # Deduplicate by ID (generic checks may overlap type-specific ones)
    seen: set[str] = set()
    unique_findings: list[_Finding] = []
    for f in findings:
        if f["id"] not in seen:
            seen.add(f["id"])
            unique_findings.append(f)

    # Map to compliance framework
    enriched = _map_to_framework(unique_findings, framework)

    # Sort: High → Medium → Low
    enriched.sort(key=lambda f: _SEVERITY_WEIGHTS.get(f["severity"], 0), reverse=True)

    summary = _build_summary(enriched, config_type)

    recommendations = [
        f["recommendation"] for f in enriched if f.get("recommendation")
    ]

    return {
        "config_type": config_type,
        "components": components,
        "summary": summary,
        "findings": enriched,
        "recommendations": recommendations,
    }
