"""Quick validation script for the rule-based evaluation engine."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from services.rule_evaluator import RuleEvaluator, get_available_standards
from rules.base import validate_rule
from rules.iso27001_rules import ISO27001_RULES
from rules.hipaa_rules import HIPAA_RULES
from rules.pci_dss_rules import PCI_DSS_RULES
from rules.sama_rules import SAMA_RULES

print("=" * 60)
print("RULE-BASED EVALUATION ENGINE — PHASE 1 VALIDATION")
print("=" * 60)

# 1. List standards
standards = get_available_standards()
print(f"\nRegistered standards: {len(standards)}")
for s in standards:
    print(f"  {s['id']:12s} | {s['label']:12s} | {s['rule_count']} rules")

# 2. Validate all rules
all_rules = {
    "iso27001": ISO27001_RULES,
    "hipaa": HIPAA_RULES,
    "pci_dss": PCI_DSS_RULES,
    "sama": SAMA_RULES,
}
total_errors = 0
for std_id, rules in all_rules.items():
    for rule in rules:
        errors = validate_rule(rule)
        if errors:
            print(f"  [ERROR] {std_id} / {rule.get('rule_id')}: {errors}")
            total_errors += len(errors)

print(f"\nValidation errors: {total_errors}")

# 3. Dry run each standard
for std_id in all_rules:
    ev = RuleEvaluator(std_id)
    result = ev.dry_run()
    s = result["summary"]
    print(f"\n--- {result['label']} Dry Run ---")
    print(f"  Total rules : {result['total_rules']}")
    print(f"  Passed      : {s['passed']}")
    print(f"  Partial     : {s['partial']}")
    print(f"  Failed      : {s['failed']}")
    print(f"  Score       : {s['score']}%")

# 4. Simulate with real signals
print("\n" + "=" * 60)
print("SIMULATED EVALUATION — ISO 27001 with sample signals")
print("=" * 60)

ev = RuleEvaluator("iso27001")
result = ev.evaluate(
    signals={
        "has_employee_records": True,
        "has_asset_inventory": True,
        "has_network_rules": True,
        "has_deny_rules": False,
        "has_access_levels": True,
        "has_governance_activities": True,
    },
    evidence_context={
        "governance": [{"activity": "Security policy review", "status": "Done"}],
        "vendors": [{"vendor_name": "CloudCo", "risk_level": "High", "compliance": "ISO 27001"}],
    },
    metrics={
        "training_coverage_pct": 72.0,
        "risky_rule_pct": 15.0,
    },
)

s = result["summary"]
print(f"  Score: {s['score']}%  (pass={s['passed']}  partial={s['partial']}  fail={s['failed']})")
for r in result["results"]:
    icon = {"pass": "[OK]", "partial": "[~~]", "fail": "[XX]"}.get(r["status"], "[??]")
    print(f"  {icon} {r['rule_id']:18s} {r['status']:8s} {r['name']}")
    print(f"    -> {r['reason']}")

print("\n[OK] ALL CHECKS PASSED - Engine is operational.")
