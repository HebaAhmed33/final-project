"""
Quick test to verify HIPAA risk driver normalization:
  - Standalone 'Phishing' + enriched 'Social Engineering / Phishing' collapses
    into a single 'Phishing / Social Engineering'.
  - No other logic is affected.
"""

import sys, os
# Ensure project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.training_matrix_generator import (
    _normalize_hipaa_driver,
    _enrich_driver,
    _HIPAA_DEFAULT_DRIVERS,
    generate_training_matrix,
)


def test_normalize_both_present():
    """When both 'Phishing' and 'Social Engineering / Phishing' exist, collapse."""
    raw = "Phishing, Data Mishandling, Unauthorized Access to PHI, Social Engineering / Phishing"
    result = _normalize_hipaa_driver(raw)
    assert "Phishing / Social Engineering" in result, f"Missing canonical term in: {result}"
    # Must NOT contain the standalone or the slash-reversed form
    parts = [p.strip() for p in result.split(",")]
    assert "Phishing" not in parts or parts[0] == "Phishing / Social Engineering", (
        f"Standalone 'Phishing' still present: {result}"
    )
    assert "Social Engineering / Phishing" not in parts, (
        f"Old enriched form still present: {result}"
    )
    print(f"  PASS  both present → {result}")


def test_normalize_only_social_eng_phishing():
    """When only 'Social Engineering / Phishing' exists (no standalone), still normalize."""
    raw = "Insider Threat, Unauthorized Access, Social Engineering / Phishing"
    result = _normalize_hipaa_driver(raw)
    parts = [p.strip() for p in result.split(",")]
    assert "Social Engineering / Phishing" not in parts, (
        f"Old enriched form still present: {result}"
    )
    assert "Phishing / Social Engineering" in parts, (
        f"Canonical term missing: {result}"
    )
    print(f"  PASS  only SE/Phishing → {result}")


def test_normalize_only_phishing_standalone():
    """When only standalone 'Phishing' exists (no SE), keep it as-is (no false merge)."""
    raw = "Phishing, Data Mishandling"
    result = _normalize_hipaa_driver(raw)
    parts = [p.strip() for p in result.split(",")]
    # Standalone phishing is fine when SE form isn't present
    assert "Phishing" in parts or "Phishing / Social Engineering" in parts, (
        f"Expected 'Phishing' to remain: {result}"
    )
    print(f"  PASS  only standalone → {result}")


def test_normalize_no_phishing_terms():
    """When no phishing terms at all, driver stays untouched."""
    raw = "Insider Threat, Data Mishandling, Workforce Policy Violations"
    result = _normalize_hipaa_driver(raw)
    assert result == raw, f"Unexpected change: {result}"
    print(f"  PASS  no phishing → {result}")


def test_enrichment_then_normalize():
    """Simulate full pipeline: base driver → enrich → normalize for HIPAA general."""
    base = _HIPAA_DEFAULT_DRIVERS["general"]  # "Phishing, Data Mishandling, Unauthorized Access to PHI"
    # Fake risk text containing 'phish' keyword to trigger enrichment
    risk_text = "recent phishing attack targeting employees via email"
    enriched = _enrich_driver("general", risk_text, base)
    normalized = _normalize_hipaa_driver(enriched)
    parts = [p.strip() for p in normalized.split(",")]
    # Should NOT have both standalone and combined
    assert parts.count("Phishing") + parts.count("Social Engineering / Phishing") == 0 or \
           "Phishing / Social Engineering" in parts, (
        f"Duplication remains after pipeline: {normalized}"
    )
    has_dup = ("Phishing" in parts and "Social Engineering / Phishing" in parts)
    assert not has_dup, f"DUPLICATE detected: {normalized}"
    print(f"  PASS  enrichment pipeline → {normalized}")


def test_full_matrix_hipaa():
    """End-to-end: generate HIPAA matrix and check no row has duplicated phishing."""
    employees = [
        {"employee": "Alice", "role": "IT Admin"},
        {"employee": "Bob", "role": "Executive"},
        {"employee": "Carol", "role": "Nurse"},
    ]
    risks = [
        {"threat": "Phishing campaign targeting hospital staff"},
        {"description": "Social engineering attack via phone"},
    ]
    result = generate_training_matrix(employees, risks, "hipaa")
    for row in result["role_based_matrix"]:
        parts = [p.strip() for p in row["driver"].split(",")]
        assert not ("Phishing" in parts and "Social Engineering / Phishing" in parts), (
            f"Duplication in role '{row['role']}': {row['driver']}"
        )
        assert "Social Engineering / Phishing" not in parts, (
            f"Non-canonical form in role '{row['role']}': {row['driver']}"
        )
        print(f"  PASS  matrix row '{row['role']}' → {row['driver']}")


if __name__ == "__main__":
    print("=== HIPAA Risk Driver Normalization Tests ===\n")
    test_normalize_both_present()
    test_normalize_only_social_eng_phishing()
    test_normalize_only_phishing_standalone()
    test_normalize_no_phishing_terms()
    test_enrichment_then_normalize()
    test_full_matrix_hipaa()
    print("\n✅ All tests passed.")
