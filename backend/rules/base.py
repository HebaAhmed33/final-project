"""
Base types and helpers shared across all rule-config modules.

Rule Schema
-----------
Each rule is a plain dict with the following keys:

  rule_id        (str)   Unique identifier, e.g. "ISO-RE-001".
  control_ref    (str)   Reference to the framework control, e.g. "A.6.1".
  name           (str)   Human-readable rule name.
  description    (str)   What this rule checks.
  domain         (str)   Logical domain / category.
  severity       (str)   "critical" | "high" | "medium" | "low".
  eval_type      (str)   How the rule is evaluated:
                            "evidence_keyword"  – keyword match in evidence data
                            "field_present"     – check if a field/sheet exists
                            "threshold"         – numeric threshold comparison
                            "boolean"           – simple true/false check
  eval_config    (dict)  Parameters consumed by the evaluator for this rule.
  remediation    (str)   Recommended remediation action if the rule fails.

eval_config contents vary by eval_type:

  evidence_keyword:
      keywords          (list[str])   Keywords to search for in evidence.
      evidence_sources  (list[str])   Sheet types that provide evidence.
      match_mode        (str)         "any" (default) or "all".

  field_present:
      required_fields   (list[str])   Fields that must be present.
      evidence_sources  (list[str])   Sheet types to inspect.

  threshold:
      metric            (str)         Name of the computed metric.
      operator          (str)         "gte" | "lte" | "gt" | "lt" | "eq".
      value             (float)       Threshold value.

  boolean:
      signal            (str)         Name of the boolean signal to check.
      expected          (bool)        Expected value (default: True).
"""

from __future__ import annotations

# Allowed severity levels (for future validation)
SEVERITY_LEVELS = ("critical", "high", "medium", "low")

# Allowed evaluation types
EVAL_TYPES = ("evidence_keyword", "field_present", "threshold", "boolean")


def validate_rule(rule: dict) -> list[str]:
    """
    Validate a rule dict.  Returns a list of error strings (empty = valid).
    """
    errors: list[str] = []
    for required in ("rule_id", "name", "eval_type", "eval_config", "severity"):
        if required not in rule:
            errors.append(f"Missing required key '{required}' in rule '{rule.get('rule_id', '?')}'")

    if rule.get("eval_type") and rule["eval_type"] not in EVAL_TYPES:
        errors.append(
            f"Invalid eval_type '{rule['eval_type']}' in rule '{rule.get('rule_id', '?')}'. "
            f"Must be one of {EVAL_TYPES}."
        )

    sev = (rule.get("severity") or "").lower()
    if sev and sev not in SEVERITY_LEVELS:
        errors.append(
            f"Invalid severity '{sev}' in rule '{rule.get('rule_id', '?')}'. "
            f"Must be one of {SEVERITY_LEVELS}."
        )

    return errors
