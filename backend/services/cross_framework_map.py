"""
Cross-Framework Control Mapping — GRC Intelligence Layer.

Maps ISO 27001 Annex A controls to equivalent controls in PCI DSS, HIPAA,
NIST CSF, CIS, and SAMA.  Designed for extensibility: add a new framework
by appending a key to each entry.

Usage:
    from services.cross_framework_map import expand_iso_controls

    result = expand_iso_controls(["A.5.15", "A.8.24"])
    # result = [
    #   { iso: "A.5.15", pci_dss: ["7.1","7.2"], hipaa: ["Access Control §164.312(a)"], ... },
    #   ...
    # ]
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Master mapping: ISO Annex A → other frameworks
# ---------------------------------------------------------------------------
# Each key is the ISO 27001:2022 Annex A control reference (short form).
# Values contain lists of equivalent control IDs in other frameworks.

_ISO_CROSS_MAP: dict[str, dict[str, list[str]]] = {
    # ── A.5 Organizational Controls ──────────────────────────────────────
    "A.5.1": {
        "pci_dss": ["12.1", "12.2"],
        "hipaa":   ["§164.308(a)(1) — Security Management Process"],
        "nist":    ["ID.GV-1", "ID.GV-2"],
        "cis":     ["CIS 1.1"],
    },
    "A.5.2": {
        "pci_dss": ["12.4"],
        "hipaa":   ["§164.308(a)(2) — Assigned Security Responsibility"],
        "nist":    ["ID.GV-2", "ID.AM-6"],
        "cis":     ["CIS 17.1"],
    },
    "A.5.10": {
        "pci_dss": ["12.3"],
        "hipaa":   ["§164.310(d)(1) — Device and Media Controls"],
        "nist":    ["PR.DS-3"],
        "cis":     ["CIS 3.1"],
    },
    "A.5.15": {
        "pci_dss": ["7.1", "7.2", "7.3"],
        "hipaa":   ["§164.312(a)(1) — Access Control"],
        "nist":    ["PR.AC-1", "PR.AC-4"],
        "cis":     ["CIS 6.1", "CIS 6.2"],
    },
    "A.5.16": {
        "pci_dss": ["8.1", "8.2"],
        "hipaa":   ["§164.312(d) — Person or Entity Authentication"],
        "nist":    ["PR.AC-1", "PR.AC-7"],
        "cis":     ["CIS 5.1", "CIS 5.2"],
    },
    "A.5.17": {
        "pci_dss": ["8.2", "8.3", "8.5"],
        "hipaa":   ["§164.312(d) — Authentication"],
        "nist":    ["PR.AC-1", "PR.AC-7"],
        "cis":     ["CIS 5.2", "CIS 5.3"],
    },
    "A.5.18": {
        "pci_dss": ["7.1", "7.2"],
        "hipaa":   ["§164.312(a)(1) — Access Control"],
        "nist":    ["PR.AC-4"],
        "cis":     ["CIS 6.1"],
    },
    "A.5.19": {
        "pci_dss": ["12.8", "12.9"],
        "hipaa":   ["§164.308(b)(1) — Business Associate Contracts"],
        "nist":    ["ID.SC-1", "ID.SC-2"],
        "cis":     ["CIS 15.1"],
    },
    "A.5.20": {
        "pci_dss": ["12.8.2"],
        "hipaa":   ["§164.308(b)(1) — BA Agreements"],
        "nist":    ["ID.SC-3"],
        "cis":     ["CIS 15.2"],
    },
    "A.5.21": {
        "pci_dss": ["12.8.4", "12.8.5"],
        "hipaa":   ["§164.308(b)(3) — Written Contract"],
        "nist":    ["ID.SC-4"],
        "cis":     ["CIS 15.4"],
    },
    "A.5.22": {
        "pci_dss": ["12.8.1"],
        "hipaa":   ["§164.308(b)(1)"],
        "nist":    ["ID.SC-2"],
        "cis":     ["CIS 15.3"],
    },
    "A.5.23": {
        "pci_dss": ["12.10"],
        "hipaa":   ["§164.308(a)(6) — Security Incident Procedures"],
        "nist":    ["RS.RP-1"],
        "cis":     ["CIS 17.4"],
    },
    "A.5.24": {
        "pci_dss": ["12.10.1"],
        "hipaa":   ["§164.308(a)(6)(i) — Response and Reporting"],
        "nist":    ["RS.RP-1", "RS.CO-1"],
        "cis":     ["CIS 17.1", "CIS 17.2"],
    },

    # ── A.6 People Controls ──────────────────────────────────────────────
    "A.6.1": {
        "pci_dss": ["12.7"],
        "hipaa":   ["§164.308(a)(3)(ii)(B) — Workforce Clearance"],
        "nist":    ["PR.IP-11"],
        "cis":     ["CIS 14.1"],
    },
    "A.6.2": {
        "pci_dss": ["12.6"],
        "hipaa":   ["§164.308(a)(5) — Security Awareness Training"],
        "nist":    ["PR.AT-1", "PR.AT-2"],
        "cis":     ["CIS 14.1", "CIS 14.2"],
    },
    "A.6.3": {
        "pci_dss": ["12.6.1", "12.6.2"],
        "hipaa":   ["§164.308(a)(5)(i) — Security Awareness Training"],
        "nist":    ["PR.AT-1"],
        "cis":     ["CIS 14.2", "CIS 14.9"],
    },
    "A.6.4": {
        "pci_dss": ["12.8.3"],
        "hipaa":   ["§164.308(a)(1)(ii)(C) — Sanction Policy"],
        "nist":    ["PR.IP-11"],
        "cis":     ["CIS 14.1"],
    },
    "A.6.5": {
        "pci_dss": ["12.7.1"],
        "hipaa":   ["§164.308(a)(3)(ii)(A) — Authorization/Supervision"],
        "nist":    ["PR.IP-11"],
        "cis":     ["CIS 14.1"],
    },
    "A.6.6": {
        "pci_dss": ["12.1.1"],
        "hipaa":   ["§164.308(a)(5)(ii)(B) — Security Reminders"],
        "nist":    ["PR.AT-1"],
        "cis":     ["CIS 14.3"],
    },
    "A.6.7": {
        "pci_dss": ["12.3.8"],
        "hipaa":   ["§164.310(b) — Workstation Use"],
        "nist":    ["PR.AC-3"],
        "cis":     ["CIS 14.7"],
    },

    # ── A.7 Physical Controls ────────────────────────────────────────────
    "A.7.1": {
        "pci_dss": ["9.1"],
        "hipaa":   ["§164.310(a)(1) — Facility Access Controls"],
        "nist":    ["PR.AC-2"],
        "cis":     ["CIS 1.4"],
    },
    "A.7.2": {
        "pci_dss": ["9.1.1", "9.2"],
        "hipaa":   ["§164.310(a)(2)(ii) — Facility Security Plan"],
        "nist":    ["PR.AC-2"],
        "cis":     ["CIS 1.4"],
    },
    "A.7.3": {
        "pci_dss": ["9.1.2", "9.1.3"],
        "hipaa":   ["§164.310(a)(2)(iii) — Access Control & Validation"],
        "nist":    ["PR.AC-2"],
        "cis":     ["CIS 1.4"],
    },
    "A.7.4": {
        "pci_dss": ["9.1.1"],
        "hipaa":   ["§164.310(a)(2)(iii)"],
        "nist":    ["DE.CM-2"],
        "cis":     ["CIS 1.5"],
    },

    # ── A.8 Technological Controls ───────────────────────────────────────
    "A.8.1": {
        "pci_dss": ["6.2", "6.4"],
        "hipaa":   ["§164.312(a)(2)(i) — Unique User Identification"],
        "nist":    ["PR.AC-1"],
        "cis":     ["CIS 5.1"],
    },
    "A.8.2": {
        "pci_dss": ["7.1", "7.2"],
        "hipaa":   ["§164.312(a)(1) — Access Control"],
        "nist":    ["PR.AC-4"],
        "cis":     ["CIS 6.1", "CIS 6.8"],
    },
    "A.8.5": {
        "pci_dss": ["8.1", "8.5"],
        "hipaa":   ["§164.312(d) — Person or Entity Authentication"],
        "nist":    ["PR.AC-7"],
        "cis":     ["CIS 5.2"],
    },
    "A.8.8": {
        "pci_dss": ["6.1", "6.2"],
        "hipaa":   ["§164.308(a)(1)(ii)(A) — Risk Analysis"],
        "nist":    ["ID.RA-1", "DE.CM-8"],
        "cis":     ["CIS 7.1", "CIS 7.4"],
    },
    "A.8.9": {
        "pci_dss": ["2.2"],
        "hipaa":   ["§164.312(a)(2)(iv) — Encryption and Decryption"],
        "nist":    ["PR.IP-1"],
        "cis":     ["CIS 4.1"],
    },
    "A.8.15": {
        "pci_dss": ["10.1", "10.2", "10.3"],
        "hipaa":   ["§164.312(b) — Audit Controls"],
        "nist":    ["DE.AE-3", "PR.PT-1"],
        "cis":     ["CIS 8.1", "CIS 8.2"],
    },
    "A.8.16": {
        "pci_dss": ["10.6", "10.7"],
        "hipaa":   ["§164.312(b) — Audit Controls"],
        "nist":    ["DE.AE-2", "DE.CM-1"],
        "cis":     ["CIS 8.5", "CIS 8.11"],
    },
    "A.8.20": {
        "pci_dss": ["1.1", "1.2", "1.3"],
        "hipaa":   ["§164.312(e)(1) — Transmission Security"],
        "nist":    ["PR.AC-5"],
        "cis":     ["CIS 12.1"],
    },
    "A.8.21": {
        "pci_dss": ["1.1.6", "2.3"],
        "hipaa":   ["§164.312(e)(1) — Transmission Security"],
        "nist":    ["PR.DS-2", "PR.AC-5"],
        "cis":     ["CIS 12.4"],
    },
    "A.8.22": {
        "pci_dss": ["1.2", "1.3"],
        "hipaa":   ["§164.312(e)(1) — Transmission Security"],
        "nist":    ["PR.AC-5"],
        "cis":     ["CIS 12.2"],
    },
    "A.8.23": {
        "pci_dss": ["1.3.5"],
        "hipaa":   ["§164.312(e)(2)(ii) — Encryption"],
        "nist":    ["PR.DS-2"],
        "cis":     ["CIS 9.2"],
    },
    "A.8.24": {
        "pci_dss": ["3.4", "4.1"],
        "hipaa":   ["§164.312(a)(2)(iv) — Encryption and Decryption", "§164.312(e)(2)(ii)"],
        "nist":    ["PR.DS-1", "PR.DS-2"],
        "cis":     ["CIS 3.6", "CIS 3.7"],
    },
}

# Supported frameworks (for future extensibility)
SUPPORTED_FRAMEWORKS = ["iso27001", "pci_dss", "hipaa", "nist", "cis"]

FRAMEWORK_LABELS = {
    "iso27001": "ISO 27001",
    "pci_dss":  "PCI DSS",
    "hipaa":    "HIPAA",
    "nist":     "NIST CSF",
    "cis":      "CIS Controls",
    "sama":     "SAMA CSF",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _normalize_control_ref(raw: str) -> str:
    """Normalize 'ISO-A5.15-01' or 'A.5.15' or 'a5.15' to 'A.5.15'."""
    import re
    cleaned = raw.strip().upper().replace("ISO-", "").replace("_", ".")
    # Remove trailing -01, -02 suffixes
    cleaned = re.sub(r"-\d+$", "", cleaned)
    # Ensure dot between letter and number: A515 -> A.5.15
    if cleaned and not "." in cleaned:
        m = re.match(r"([A-Z])(\d)(\d+)", cleaned)
        if m:
            cleaned = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    return cleaned


def get_cross_framework_mapping(iso_control: str) -> dict[str, list[str]]:
    """Get mapping for a single ISO control to all other frameworks."""
    ref = _normalize_control_ref(iso_control)
    return _ISO_CROSS_MAP.get(ref, {})


def expand_iso_controls(iso_controls: list[str]) -> list[dict]:
    """
    Expand a list of ISO control references to all mapped frameworks.

    Returns list of dicts:
        { iso: "A.5.15", pci_dss: [...], hipaa: [...], nist: [...], cis: [...] }
    """
    results = []
    for raw in iso_controls:
        ref = _normalize_control_ref(raw)
        mapping = _ISO_CROSS_MAP.get(ref, {})
        entry = {"iso": ref}
        for fw in ["pci_dss", "hipaa", "nist", "cis"]:
            entry[fw] = mapping.get(fw, [])
        results.append(entry)
    return results


def map_risks_cross_framework(risks: list[dict]) -> list[dict]:
    """
    Take parsed high-risk rows with iso_controls and expand to
    multi-framework mapping.

    Each risk dict should have:
        risk_id, risk_statement, iso_controls: list[str], rationale

    Returns enriched list with pci_controls, hipaa_controls, etc.
    """
    enriched = []
    for risk in risks:
        iso_ctrls = risk.get("iso_controls", [])
        expanded = expand_iso_controls(iso_ctrls)

        pci_all, hipaa_all, nist_all, cis_all = [], [], [], []
        for exp in expanded:
            pci_all.extend(exp.get("pci_dss", []))
            hipaa_all.extend(exp.get("hipaa", []))
            nist_all.extend(exp.get("nist", []))
            cis_all.extend(exp.get("cis", []))

        enriched.append({
            **risk,
            "pci_controls":   sorted(set(pci_all)),
            "hipaa_controls": sorted(set(hipaa_all)),
            "nist_controls":  sorted(set(nist_all)),
            "cis_controls":   sorted(set(cis_all)),
            "cross_framework_coverage": {
                "iso":   len(iso_ctrls),
                "pci":   len(set(pci_all)),
                "hipaa": len(set(hipaa_all)),
                "nist":  len(set(nist_all)),
                "cis":   len(set(cis_all)),
            },
        })
    return enriched
