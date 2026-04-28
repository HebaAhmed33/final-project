"""
Contextual Risk Generator — produces realistic, asset-aware risks.

Replaces the old generic generate_risks_from_data with logic that:
  1. Iterates individual assets/vendors/employees from uploaded sheets
  2. Maps asset types to specific threats
  3. Cross-references missing/weak controls
  4. Assigns dynamic owners
  5. Generates 15–25+ enterprise-grade risk statements

Robust to any column naming — uses multi-key extraction with safe defaults.
Framework-aware — tailors control wording based on active framework priority.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Robust field extraction — resilient to any Excel column naming
# ---------------------------------------------------------------------------
# Each tuple defines (canonical_key, [alias_keys...]) probed in order.
# First non-empty value wins.  If all are empty, the default is used.

def _get(row: dict, *keys: str, default: str = "") -> str:
    """Extract a field from a row dict trying multiple candidate keys."""
    for k in keys:
        val = row.get(k)
        if val is not None:
            s = str(val).strip()
            if s and s.lower() not in ("nan", "none", "null", "n/a", "na", "—", "-"):
                return s
    return default





# ---------------------------------------------------------------------------
# Asset-type classification
# ---------------------------------------------------------------------------

def _classify_asset(name: str, asset_type: str, os_field: str) -> str:
    blob = f"{name} {asset_type} {os_field}".lower()
    if any(k in blob for k in ("server", "host", "vm", "esxi", "hypervisor")):
        return "Server"
    if any(k in blob for k in ("database", "db", "sql", "oracle", "mongo", "postgres", "mysql", "redis")):
        return "Database"
    if any(k in blob for k in ("dns", "domain name", "bind", "named")):
        return "DNS"
    if any(k in blob for k in ("firewall", "fw", "router", "switch", "gateway", "load balancer", "lb")):
        return "Network Device"
    if any(k in blob for k in ("laptop", "desktop", "workstation", "endpoint", "pc")):
        return "Endpoint"
    if any(k in blob for k in ("app", "web", "api", "portal", "saas", "crm", "erp")):
        return "Application"
    if any(k in blob for k in ("storage", "nas", "san", "backup", "tape")):
        return "Storage"
    if any(k in blob for k in ("linux", "ubuntu", "centos", "rhel", "debian")):
        return "Server"
    if any(k in blob for k in ("windows server",)):
        return "Server"
    if any(k in blob for k in ("windows", "macos", "mac os")):
        return "Endpoint"
    return "IT Asset"


# ---------------------------------------------------------------------------
# Threat mapping per asset class
# ---------------------------------------------------------------------------
# Each entry now has:
#   threat_label  — short, categorized (e.g. "Remote Code Execution")
#   statement_tpl — contextual risk statement template with {asset} placeholder
#   control       — specific, actionable control recommendation

_THREAT_MAP: dict[str, list[dict]] = {
    "Server": [
        {"threat_label": "Remote Code Execution",
         "statement_tpl": "Exploitation of unpatched OS vulnerabilities on {asset} enabling remote code execution and lateral movement",
         "control": "Deploy automated patch management and scheduled vulnerability scanning",
         "impact": "Full server compromise leading to data exfiltration and lateral movement"},
        {"threat_label": "Credential Theft",
         "statement_tpl": "Unauthorized administrative access to {asset} due to weak or shared credentials",
         "control": "Enforce MFA and deploy privileged access management (PAM) for all server accounts",
         "impact": "Complete administrative takeover of server infrastructure"},
        {"threat_label": "Malware",
         "statement_tpl": "Malware propagation through unprotected services on {asset} leading to service disruption",
         "control": "Deploy EDR agents and enforce application whitelisting on all servers",
         "impact": "Service disruption and potential data destruction"},
    ],
    "Database": [
        {"threat_label": "SQL Injection",
         "statement_tpl": "Data breach in {asset} through SQL injection exploiting insufficient input validation",
         "control": "Enforce parameterized queries, deploy WAF, and perform quarterly DAST scans",
         "impact": "Mass data breach exposing sensitive records"},
        {"threat_label": "Data Exfiltration",
         "statement_tpl": "Exposure of sensitive records in {asset} due to missing encryption at rest",
         "control": "Enable transparent data encryption (TDE) and centralized key management",
         "impact": "Regulatory non-compliance and data exposure in case of theft"},
        {"threat_label": "Privilege Abuse",
         "statement_tpl": "Insider data theft from {asset} enabled by excessive database privileges",
         "control": "Apply least-privilege database roles and enable query-level audit logging",
         "impact": "Unauthorized data modification or exfiltration by insiders"},
    ],
    "DNS": [
        {"threat_label": "DNS Hijacking",
         "statement_tpl": "Traffic redirection to malicious endpoints via DNS record manipulation on {asset}",
         "control": "Implement DNSSEC, enable DNS change alerting, and restrict zone transfer access",
         "impact": "Credential theft and phishing via spoofed domains"},
        {"threat_label": "DNS Poisoning",
         "statement_tpl": "Cache poisoning of {asset} corrupting name resolution for internal services",
         "control": "Enable DNSSEC validation, restrict recursive queries, and harden resolver configuration",
         "impact": "Users redirected to attacker-controlled infrastructure"},
    ],
    "Network Device": [
        {"threat_label": "Misconfiguration",
         "statement_tpl": "Network-wide compromise through exploitation of default credentials on {asset}",
         "control": "Enforce credential rotation policy and disable all default/factory accounts",
         "impact": "Network-wide compromise through pivoting from core devices"},
        {"threat_label": "Unauthorized Change",
         "statement_tpl": "Traffic interception or segmentation bypass due to unauthorized configuration changes on {asset}",
         "control": "Implement change management workflow and enable configuration audit logging",
         "impact": "Traffic interception or network segmentation bypass"},
    ],
    "Endpoint": [
        {"threat_label": "Ransomware",
         "statement_tpl": "Ransomware infection on {asset} via phishing or malicious download, resulting in severe service disruption and data unavailability",
         "control": "Deploy EDR, enforce application whitelisting, and enable email attachment sandboxing",
         "impact": "Workstation encryption leading to operational downtime, potential lateral spread, and patient safety impact if critical systems are affected"},
        {"threat_label": "Data Leakage",
         "statement_tpl": "Sensitive data exfiltration from {asset} through removable media or unauthorized cloud sync",
         "control": "Implement DLP policies, restrict USB access, and block unapproved cloud storage",
         "impact": "Loss of sensitive corporate data and IP theft"},
    ],
    "Application": [
        {"threat_label": "Broken Access Control",
         "statement_tpl": "Unauthorized access to sensitive data in {asset} due to misconfigured role-based access controls",
         "control": "Implement RBAC with periodic access reviews and enforce OWASP secure SDLC",
         "impact": "Unauthorized access to application data and functions"},
        {"threat_label": "API Abuse",
         "statement_tpl": "Service degradation and data scraping in {asset} through unprotected API endpoints",
         "control": "Deploy API gateway with rate limiting, OAuth authentication, and schema validation",
         "impact": "Data scraping, service degradation, or unauthorized operations"},
    ],
    "Storage": [
        {"threat_label": "Unauthorized Access",
         "statement_tpl": "Exposure of historical and backup data in {asset} due to insufficient access controls",
         "control": "Encrypt all backups at rest and enforce role-based access to storage systems",
         "impact": "Exposure of historical data including deleted records"},
    ],
    "IT Asset": [
        {"threat_label": "Unmanaged Asset Exposure",
         "statement_tpl": "Unmonitored attack surface from unmanaged IT asset '{asset}' bypassing security controls",
         "control": "Maintain automated asset discovery and enforce CMDB onboarding policies",
         "impact": "Unmonitored attack surface expanding organizational risk"},
        {"threat_label": "Unauthorized System Deployment",
         "statement_tpl": "Unauthorized deployment of '{asset}' creating an undocumented entry point into the environment",
         "control": "Implement network access control (NAC) and strict provisioning workflows",
         "impact": "Unauthorized access vectors bypassing perimeter defenses"},
        {"threat_label": "Asset Visibility Gap",
         "statement_tpl": "Lack of security monitoring and visibility on untracked asset '{asset}'",
         "control": "Deploy agent-based or network-level discovery tools to ensure comprehensive asset coverage",
         "impact": "Delayed threat detection and unmitigated vulnerabilities"},
        {"threat_label": "Untracked SaaS Usage",
         "statement_tpl": "Unapproved utilization of SaaS platform '{asset}' leading to unmonitored data flows outside the corporate boundary",
         "control": "Deploy CASB and enforce cloud application discovery and governance",
         "impact": "Data exposure and compliance violations from shadow cloud adoption"},
    ],
}

# ---------------------------------------------------------------------------
# Owner mapping
# ---------------------------------------------------------------------------

_OWNER_MAP: dict[str, str] = {
    "Server": "IT Operations",
    "Database": "Database Administration",
    "DNS": "IT Operations",
    "Network Device": "Network / DevOps",
    "Endpoint": "IT Support",
    "Application": "Application Security",
    "Storage": "IT Operations",
    "IT Asset": "IT Team",
    "Vendor": "IT Security / Procurement",
    "User": "IT Security / HR",
    "Governance": "IT Governance",
    "Network": "Network / DevOps",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lh(threat: str, impact: str) -> int:
    t = (threat + " " + impact).lower()
    if any(k in t for k in ("remote code", "ransomware", "active exposure")):
        return 4
    if any(k in t for k in ("injection", "credential", "misconfiguration", "breach")):
        return 3
    return 2


def _imp(threat: str, impact: str) -> int:
    t = (threat + " " + impact).lower()
    if any(k in t for k in ("destruction", "takeover", "ransomware", "safety")):
        return 5
    if any(k in t for k in ("breach", "exfiltration", "compromise")):
        return 4
    return 3


def _level(l: int, i: int) -> str:
    s = l * i
    if s >= 16:
        return "Critical"
    if s >= 10:
        return "High"
    if s >= 5:
        return "Medium"
    return "Low"


def _risk_entry(rid: int, statement: str, asset: str, threat_label: str,
                lh: int, imp: int, control: str, owner: str,
                category: str, source: str, detail: str) -> dict:
    lvl = _level(lh, imp)
    
    # ── Map Threat to SoA Control IDs ──
    threat_control_map = {
        "SQL Injection": ["A.8.28"],
        "Broken Access Control": ["A.8.3"],
        "Ransomware": ["A.8.7"],
        "API Abuse": ["A.8.23", "A.8.28"],
        "Misconfiguration": ["A.8.9"],
        "Data Exfiltration": ["A.8.12"],
        "Supply Chain Attack": ["A.5.19"],
        "Third-Party Compliance Risk": ["A.5.1", "A.5.20"],
        "Business Continuity Failure": ["A.5.30"]
    }
    
    control_ids = threat_control_map.get(threat_label, [])

    return {
        "risk_id": f"R{rid}",
        "risk_name": statement,
        "risk_statement": statement,
        "asset": asset,
        "asset_type": category,
        "threat": threat_label,
        "likelihood": lh,
        "impact": imp,
        "risk_level": lvl,
        "control": control,
        "controls": control,
        "control_id": control_ids,
        "owner": owner,
        "category": category,
        "source": source,
        "source_label": "Generated",
        "detail": detail,
        "mitigation": control,
    }


def _is_valid(r: dict) -> bool:
    """Reject any risk with empty or generic placeholder fields."""
    bad_values = {"", "—", "Unspecified Threat", "Mapped via ISO27001",
                  "Mapped via ISO 27001", "Non-compliance with framework requirements"}
    for key in ("threat", "asset", "owner", "control", "risk_statement"):
        val = (r.get(key) or "").strip()
        if not val or val in bad_values:
            return False
    return True


def _stmt_words(text: str) -> set[str]:
    """Extract significant words (≥4 chars) from a risk statement."""
    return {w.lower() for w in text.split() if len(w) >= 4}


def _merge_duplicate_root_causes(risks: list[dict]) -> list[dict]:
    """
    Merge risks that describe the same root cause.

    Two risks are duplicates when they share:
      1. The same threat label, AND
      2. The same asset (different assets are distinct risks), AND
      3. ≥3 significant keywords in common in their statements.

    The entry with the higher risk score (likelihood × impact) is kept;
    the detail text from the weaker entry is appended.
    """
    if len(risks) <= 1:
        return risks

    absorbed: set[int] = set()
    result: list[dict] = []

    for i in range(len(risks)):
        if i in absorbed:
            continue
        base = dict(risks[i])  # working copy
        base_threat = base.get("threat", "").lower()
        base_asset = base.get("asset", "").lower()
        base_words = _stmt_words(base.get("risk_statement", ""))
        base_score = base.get("likelihood", 0) * base.get("impact", 0)

        for j in range(i + 1, len(risks)):
            if j in absorbed:
                continue
            cand = risks[j]
            if cand.get("threat", "").lower() != base_threat:
                continue
            # Different specific assets are separate risks — do NOT merge
            if cand.get("asset", "").lower() != base_asset:
                continue

            overlap = len(base_words & _stmt_words(cand.get("risk_statement", "")))
            if overlap < 3:
                continue

            # Duplicate found — absorb weaker entry
            cand_score = cand.get("likelihood", 0) * cand.get("impact", 0)
            if cand_score > base_score:
                # Candidate is stronger — promote it
                cand_detail = base.get("detail", "")
                base = dict(cand)
                base_score = cand_score
                base_words = _stmt_words(base.get("risk_statement", ""))
                extra_detail = cand_detail
            else:
                extra_detail = cand.get("detail", "")

            if extra_detail and extra_detail not in base.get("detail", ""):
                base["detail"] = base.get("detail", "") + " | " + extra_detail

            absorbed.add(j)

        result.append(base)

    return result


# ---------------------------------------------------------------------------
# Public API — replaces old generate_risks_from_data
# ---------------------------------------------------------------------------

def generate_risks_from_data(
    routing: dict,
    controls: list[dict],
    present_types: set[str],
    all_sheets: list[dict] | None = None,
    framework_id: str = "iso27001",
) -> list[dict]:
    """
    Generate 15–25+ realistic, context-aware risk entries from:
      1. Individual assets (per-row)
      2. Individual vendors (per-row)
      3. Employee / people gaps
      4. Network rule weaknesses
      5. Missing/partial high-severity controls
    """
    framework_id = framework_id.lower()
    risks: list[dict] = []
    rid = 1
    seen_sigs: set[str] = set()  # dedup key

    def _add(r: dict, sig: str | None = None):
        nonlocal rid
        key = sig or f"{r['asset']}|{r['threat']}"
        if key in seen_sigs:
            return
        
        # Light contextual enrichment based on framework
        if framework_id == "hipaa":
            stmt = r["risk_statement"]
            asset_str = str(r.get("asset", "")).lower()
            
            health_keywords = {
                "patient", "ehr", "lab", "pacs", "billing", 
                "claims", "medical records", "pharmacy", 
                "telehealth", "backup"
            }
            
            combined_text = f"{stmt} {asset_str}".lower()
            if any(kw in combined_text for kw in health_keywords):
                if " data " in stmt or " data" in stmt or "Data " in stmt:
                    stmt = stmt.replace(" data ", " ePHI/patient data ").replace(" data", " ePHI/patient data").replace("Data ", "ePHI/Patient Data ")
                
                if "unmanaged IT asset" in stmt or "untracked asset" in stmt:
                    if "ehr" in asset_str or "medical records" in asset_str:
                        stmt = stmt.replace("IT asset", "clinical system").replace("untracked asset", "untracked clinical system")
                    elif "billing" in asset_str or "claims" in asset_str:
                        stmt = stmt.replace("IT asset", "billing system").replace("untracked asset", "untracked billing system")
                    elif "telehealth" in asset_str:
                        stmt = stmt.replace("IT asset", "patient care platform").replace("untracked asset", "untracked patient care platform")
                    elif "pacs" in asset_str or "lab" in asset_str or "pharmacy" in asset_str:
                        stmt = stmt.replace("IT asset", "diagnostic system").replace("untracked asset", "untracked diagnostic system")

                if "Unauthorized deployment" in stmt:
                    if "ehr" in asset_str or "medical records" in asset_str:
                        stmt = stmt.replace("environment", "clinical environment")
                    elif "billing" in asset_str or "claims" in asset_str:
                        stmt = stmt.replace("environment", "financial environment")
                    elif "telehealth" in asset_str:
                        stmt = stmt.replace("environment", "patient care environment")
                
                r["risk_statement"] = stmt

        seen_sigs.add(key)
        risks.append(r)
        rid += 1

    # ── Collect raw rows from all_sheets or routing ───────────────────────
    asset_rows: list[dict] = []
    vendor_rows: list[dict] = []
    employee_rows: list[dict] = []

    if all_sheets:
        for s in all_sheets:
            t = s.get("type", "")
            if t in ("assets", "applications"):
                asset_rows.extend(s.get("rows", []))
            elif t == "vendors":
                vendor_rows.extend(s.get("rows", []))
            elif t == "employees":
                employee_rows.extend(s.get("rows", []))

    # ── Build missing-control lookup ─────────────────────────────────────
    missing_ctrls = [
        c for c in controls
        if c.get("status") in ("missing", "partial")
    ]
    missing_names_lower = " ".join(
        (c.get("name", "") + " " + c.get("domain", "")).lower()
        for c in missing_ctrls
    )

    def _has_gap(keyword: str) -> bool:
        return keyword.lower() in missing_names_lower

    # ══════════════════════════════════════════════════════════════════════
    # 1. PER-ASSET RISKS
    # ══════════════════════════════════════════════════════════════════════
    for row in asset_rows:
        name = _get(row, "asset_name", "app_name", "name", "hostname",
                    "device_name", "device", "system", "system_name",
                    "host", "equipment", default="Unnamed Asset")
        atype = _get(row, "asset_type", "app_type", "type", "category",
                     "device_type", "classification")
        os_f = _get(row, "os", "operating_system", "platform")
        crit = _get(row, "criticality", "critical", "importance",
                    "risk_level", "priority", "sensitivity").lower()
        owner_f = _get(row, "owner", "asset_owner", "custodian",
                       "responsible", "assigned_to", "manager")

        cls = _classify_asset(name, atype, os_f)
        threats = _THREAT_MAP.get(cls, _THREAT_MAP["IT Asset"])

        # Cycle through IT Asset threats based on asset name length to diversify
        if cls == "IT Asset" and len(threats) > 2:
            shift = len(name) % len(threats)
            threats = threats[shift:] + threats[:shift]

        # Pick 1-2 threats per asset depending on criticality
        pick = 2 if crit in ("high", "critical") else 1

        for tinfo in threats[:pick]:
            lh = _lh(tinfo["threat_label"], tinfo["impact"])
            if crit in ("high", "critical"):
                lh = min(4, lh + 1)
            imp = _imp(tinfo["threat_label"], tinfo["impact"])

            ctrl_text = tinfo["control"]

            stmt = tinfo["statement_tpl"].format(asset=name)
            detail = f"Asset: {name} ({cls}). {tinfo['impact']}."
            own = owner_f if owner_f else _OWNER_MAP.get(cls, "IT Team")

            _add(_risk_entry(
                rid, stmt, name, tinfo["threat_label"], lh, imp,
                ctrl_text, own, cls, "asset_analysis", detail,
            ))

        # Unowned-asset risk
        if not owner_f:
            _add(_risk_entry(
                rid,
                f"Delayed incident response for {cls.lower()} '{name}' due to unassigned asset ownership",
                name, "Accountability Gap",
                3, 3,
                "Assign an accountable owner and define incident escalation path",
                "IT Governance", "Asset Management", "asset_analysis",
                f"{name} has no assigned owner — delays triage and remediation.",
            ), sig=f"unowned|{name}")

    # ══════════════════════════════════════════════════════════════════════
    # 2. PER-VENDOR RISKS  (driven by compliance status, NOT criticality)
    # ══════════════════════════════════════════════════════════════════════
    for row in vendor_rows:
        vname = _get(row, "vendor_name", "name", "vendor", "supplier",
                     "company", "partner", "provider", "service_provider",
                     "third_party", default="Unknown Vendor")
        vcomp = _get(row, "compliance", "compliance_status", "compliant",
                     "certified", "certification", "audit_status",
                     "certifications").lower()
        vservice = _get(row, "service_type", "service", "category",
                        "scope", "engagement", "type",
                        default="third-party services")
        vcrit = _get(row, "risk_level", "risk", "risk_rating",
                     "criticality", "priority", "vendor_risk").lower()

        # ── Compliant vendor → dependency/monitoring risk ONLY ─────────
        #    Check this FIRST so compliant vendors never fall into higher tiers.
        if vcomp in ("compliant", "certified", "approved", "passed", "yes"):
            if vcrit in ("high", "critical"):
                _add(_risk_entry(
                    rid,
                    f"High-dependency risk on vendor '{vname}' ({vservice}) — compliant but critical to operations",
                    vname, "Vendor Dependency",
                    1, 3,
                    "Monitor vendor SLA performance and maintain contingency plan for service disruption",
                    "IT Security / Procurement", "Vendor", "vendor_analysis",
                    f"Vendor '{vname}' is compliant but classified as high-criticality — monitor dependency.",
                ))
            # Compliant + non-critical vendors generate no risk entry.

        # ── Non-Compliant vendor → High/Critical vendor risk ──────────
        elif vcomp in ("non-compliant", "non compliant", "no", "failed"):
            _add(_risk_entry(
                rid,
                f"Supply chain compromise through non-compliant vendor '{vname}' providing {vservice}",
                vname, "Supply Chain Attack",
                3, 4,
                "Conduct immediate vendor security assessment and enforce contractual security clauses",
                "IT Security / Procurement", "Vendor", "vendor_analysis",
                f"Vendor '{vname}' is non-compliant for {vservice} — critical supply chain risk.",
            ))
            v_control = "Require SOC 2 / ISO 27001 attestation or equivalent certification from vendor"
            if framework_id == "hipaa":
                v_control = "Require signed Business Associate Agreement (BAA) and SOC 2 / HITRUST attestation from vendor"
                
            _add(_risk_entry(
                rid,
                f"Regulatory exposure from non-compliant vendor '{vname}' handling regulated data",
                vname, "Third-Party Compliance Risk",
                2, 4,
                v_control,
                "IT Security / Procurement", "Vendor", "vendor_analysis",
                f"Vendor '{vname}' has no valid compliance certification on record.",
            ))

        # ── Review Pending / Unknown / Empty → Medium/High vendor risk ─
        #    Includes "none", "missing", empty string — treat as unverified.
        else:
            _add(_risk_entry(
                rid,
                f"Unverified compliance posture for vendor '{vname}' ({vservice}) — review pending",
                vname, "Third-Party Compliance Risk",
                2, 3,
                "Expedite vendor compliance review and establish interim monitoring controls",
                "IT Security / Procurement", "Vendor", "vendor_analysis",
                f"Vendor '{vname}' compliance status is pending review.",
            ))

    # ══════════════════════════════════════════════════════════════════════
    # 3. EMPLOYEE / PEOPLE RISKS
    # ══════════════════════════════════════════════════════════════════════
    for rr in routing.get("routing_results", []):
        if rr.get("source_type") != "employees" or rr.get("total_records", 0) == 0:
            continue
        total = rr["total_records"]
        no_train = rr.get("no_security_training", 0)
        priv = rr.get("privileged_access_count", 0)

        if no_train > 0:
            pct = round(no_train / total * 100)
            _add(_risk_entry(
                rid,
                f"Increased phishing susceptibility across workforce — {no_train} of {total} employees ({pct}%) lack security awareness training",
                "Workforce", "Phishing",
                3 if pct > 50 else 2, 4,
                "Deploy mandatory security awareness training with quarterly phishing simulations",
                "IT Security / HR", "User", "employee_analysis",
                f"{no_train} employees have no recorded security training.",
            ), sig="people|no_training")

            _add(_risk_entry(
                rid,
                f"Elevated insider threat behavior risk — {pct}% of staff untrained, increasing likelihood of privilege misuse or unmonitored data access",
                "Workforce", "Insider Threat",
                2, 4,
                "Implement role-based training program, enforce acceptable use policies, and deploy behavior monitoring",
                "IT Security / HR", "User", "employee_analysis",
                f"Large untrained workforce increases probability of behavioral risk and privilege misuse.",
            ), sig="people|insider_culture")

        if priv > 0:
            _add(_risk_entry(
                rid,
                f"Critical credential compromise risk — {priv} users hold admin/privileged access without enhanced controls",
                "Privileged Accounts", "Credential Theft",
                3, 5,
                "Enforce PAM solution, MFA on all admin accounts, and quarterly access reviews",
                "IT Security", "User", "employee_analysis",
                f"{priv} users hold privileged access; compromise = full environment takeover.",
            ), sig="people|priv_access")

    # ══════════════════════════════════════════════════════════════════════
    # 4. NETWORK RISKS
    # ══════════════════════════════════════════════════════════════════════
    for rr in routing.get("routing_results", []):
        if rr.get("source_type") != "network_rules" or rr.get("total_records", 0) == 0:
            continue
        risky = rr.get("risky_rules_count", 0)
        deny = rr.get("deny_rules_count", 0)

        if risky > 0:
            _add(_risk_entry(
                rid,
                f"Lateral movement risk enabled by {risky} overly permissive firewall rules using ANY/wildcard patterns",
                "Network Perimeter", "Misconfiguration",
                3, 4,
                "Replace wildcard rules with explicit source/destination/port definitions",
                "Network / DevOps", "Network", "network_analysis",
                f"{risky} rules use ANY/wildcard — attackers can traverse network segments.",
            ), sig="network|permissive")

            _add(_risk_entry(
                rid,
                "Covert data exfiltration channel through unrestricted outbound firewall rules",
                "Network Perimeter", "Data Exfiltration",
                2, 4,
                "Implement egress filtering and deploy outbound traffic anomaly monitoring",
                "Network / DevOps", "Network", "network_analysis",
                "Unrestricted outbound rules allow attackers to exfiltrate data undetected.",
            ), sig="network|egress")

        if deny == 0:
            _add(_risk_entry(
                rid,
                "Unrestricted network access due to default-allow posture with no explicit deny rules",
                "Network Infrastructure", "Misconfiguration",
                3, 4,
                "Implement default-deny firewall policy with explicit allow-list exceptions",
                "Network / DevOps", "Network", "network_analysis",
                "No deny rules detected — default-allow posture assumed.",
            ), sig="network|no_deny")

    # ══════════════════════════════════════════════════════════════════════
    # 5. CONTROL-GAP RISKS (missing/partial high-severity controls)
    # ══════════════════════════════════════════════════════════════════════
    _CONTROL_THREAT_MAP = {
        "patch": ("Unpatched Vulnerability",
                  "Exploitation of known CVEs in unpatched systems across the environment",
                  "Deploy automated patch management with SLA-based remediation timelines"),
        "access": ("Broken Access Control",
                   "Unauthorized access to sensitive resources due to missing access control enforcement",
                   "Implement RBAC with periodic access certification and automated provisioning"),
        "encrypt": ("Data Exposure",
                    "Sensitive data interception due to absent encryption controls on data in transit and at rest",
                    "Deploy TLS 1.3 for data in transit and AES-256 encryption for data at rest"),
        "crypto": ("Data Exposure",
                   "Data compromise due to missing or weak cryptographic protections",
                   "Implement centralized key management and enforce encryption policies"),
        "incident": ("Incident Response Failure",
                     "Delayed breach detection and containment due to absent incident response procedures",
                     "Establish and test a formal incident response plan with defined SLAs and escalation paths"),
        "backup": ("Data Loss",
                   "Permanent data loss due to missing backup and disaster recovery procedures",
                   "Implement automated daily backups with offsite replication and quarterly restore testing"),
        "monitor": ("Insufficient Monitoring",
                    "Undetected intrusions and compliance violations due to absent logging and monitoring",
                    "Deploy centralized SIEM with real-time alerting and 90-day log retention"),
        "audit": ("Compliance Violation",
                  "Regulatory violations undetected due to missing internal audit processes",
                  "Establish internal audit program with quarterly reviews and evidence collection"),
        "vendor": ("Supply Chain Attack",
                   "Supply chain compromise through unmanaged third-party vendor relationships",
                   "Implement vendor risk assessment program with annual security reviews"),
        "supplier": ("Supply Chain Attack",
                     "Supply chain compromise through unmanaged supplier relationships",
                     "Implement supplier security assessment and enforce contractual security requirements"),
        "training": ("Phishing",
                     "Increased human error and social engineering susceptibility due to absent awareness programs",
                     "Deploy role-based security awareness training with annual refreshers and testing"),
        "physical": ("Physical Intrusion",
                     "Physical intrusion or equipment theft from inadequately secured facilities",
                     "Implement physical access controls, CCTV monitoring, and visitor management"),
        "config": ("Misconfiguration",
                   "System compromise via insecure default configurations across infrastructure",
                   "Apply CIS hardening benchmarks and deploy automated configuration compliance scanning"),
        "network": ("Network Exploitation",
                    "Network-based attacks facilitated by insufficient network segmentation",
                    "Implement network segmentation with micro-segmentation for critical asset zones"),
        "malware": ("Malware",
                    "Malware propagation across unprotected endpoints and servers",
                    "Deploy next-generation antimalware with behavioral detection and automated response"),
        "asset": ("Unmanaged Asset Exposure",
                  "Expanding attack surface from untracked and unmanaged IT assets",
                  "Maintain automated asset discovery and enforce CMDB onboarding policies"),
    }

    for ctrl in missing_ctrls:
        sev = (ctrl.get("severity") or "").lower()
        if sev not in ("high", "critical"):
            continue

        ctrl_name = ctrl.get("name", "")
        domain = ctrl.get("domain") or ctrl.get("section_name", "General")
        ctrl_lower = ctrl_name.lower() + " " + domain.lower()

        threat_label = "Governance Control Gap"
        stmt_text = f"Operational risk from missing '{ctrl_name}' control in {domain}"
        control_text = f"Define, approve, and implement '{ctrl_name}' with assigned ownership and evidence collection"

        for keyword, (tl, st, ct) in _CONTROL_THREAT_MAP.items():
            if keyword in ctrl_lower:
                threat_label = tl
                stmt_text = st
                control_text = ct
                break

        lh = 3 if sev == "critical" else 2
        imp = 4 if sev == "critical" else 3
        
        if ctrl.get("status") == "partial":
            lh = max(1, lh - 1)

        _add(_risk_entry(
            rid, stmt_text, domain, threat_label, lh, imp,
            control_text, _OWNER_MAP.get("Server", "IT Team"),
            domain, "framework_gap",
            f"Control '{ctrl_name}' ({ctrl.get('rule_id', '')}) is {ctrl.get('status', 'missing')}. {ctrl.get('reason', '')}",
        ), sig=f"gap|{threat_label}")

    # ══════════════════════════════════════════════════════════════════════
    # 6. CROSS-CUTTING RISKS (always relevant when data exists)
    # ══════════════════════════════════════════════════════════════════════
    if "assets" in present_types or "applications" in present_types:
        if _has_gap("change") or _has_gap("config"):
            _add(_risk_entry(
                rid,
                "Unauthorized system modifications due to absent change management process",
                "IT Environment", "Unauthorized Change",
                2, 3,
                "Implement formal change advisory board (CAB) and automated change management workflow",
                "IT Governance", "Governance", "cross_cutting",
                "No change management evidence found; unauthorized changes may go undetected.",
            ), sig="cross|change_mgmt")

    if len(present_types) >= 2:
        if _has_gap("continuity") or _has_gap("disaster") or _has_gap("recovery"):
            _add(_risk_entry(
                rid,
                "Extended business disruption due to absent disaster recovery and continuity planning",
                "Business Operations", "Business Continuity Failure",
                2, 5,
                "Develop and test BCP/DR plans with defined RTOs, RPOs, and annual tabletop exercises",
                "IT Governance", "Governance", "cross_cutting",
                "No business continuity / disaster recovery controls evidenced.",
            ), sig="cross|bcp_dr")

    # ══════════════════════════════════════════════════════════════════════
    # POST-PROCESS: filter invalid, deduplicate root causes, re-sequence
    # ══════════════════════════════════════════════════════════════════════
    valid = [r for r in risks if _is_valid(r)]
    valid = _merge_duplicate_root_causes(valid)
    for idx, r in enumerate(valid, start=1):
        r["risk_id"] = f"R{idx}"

    return valid
