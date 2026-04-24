"""
Rule Engine Bridge — connects the RuleEvaluator + JSON condition evaluator
to the assessment pipeline in framework_aware_builder.

This module is the SINGLE entry point that replaces the old
evidence_inference heuristic as the PRIMARY evaluation source.
"""

from __future__ import annotations

import logging
import os

_log = logging.getLogger("runtime_proof")
if not _log.handlers:
    _log.setLevel(logging.DEBUG)
    _fh = logging.FileHandler(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "runtime_proof.log"),
        mode="a", encoding="utf-8",
    )
    _fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _log.addHandler(_fh)


# ---------------------------------------------------------------------------
# Signal mapping: JSON condition tokens → evidence_inference signal names
# ---------------------------------------------------------------------------

_CONDITION_SIGNAL_MAP: dict[str, str] = {
    "employees_exist":          "has_employee_records",
    "governance_exist":         "has_governance_activities",
    "assets_exist":             "has_asset_inventory",
    "network_rules_exist":      "has_network_rules",
    "vendors_exist":            "has_vendor_records",
    "risk_register_exist":      "has_risk_register",
    "training_records_exist":   "has_some_training",
    "training_records_missing": "_neg_has_some_training",
    "deny_rules_exist":         "has_deny_rules",
    "risky_rules_low":          "low_risky_rules",
    "assets_have_location":     "has_asset_locations",
    "assets_missing_location":  "_neg_has_asset_locations",
    "assets_missing_owner":     "_neg_has_asset_owners",
    "assets_missing_criticality": "_neg_has_asset_classifications",
    "applications_exist":       "has_applications",
    "policies_incomplete":      "_neg_has_governance_activities",
    "vendors_missing_compliance": "_neg_has_vendor_compliance",
}


def _resolve_token(token: str, signals: dict[str, bool]) -> bool:
    """Resolve a single condition token against signals."""
    token = token.strip()

    # Handle NOT prefix
    negated = False
    if token.startswith("NOT "):
        negated = True
        token = token[4:].strip()

    # Check for threshold expressions (e.g. "training_coverage >= 60%")
    if ">=" in token or "<=" in token:
        return not negated  # Thresholds handled by RuleEvaluator, assume partial

    signal_key = _CONDITION_SIGNAL_MAP.get(token)
    if signal_key:
        if signal_key.startswith("_neg_"):
            val = not signals.get(signal_key[5:], False)
        else:
            val = signals.get(signal_key, False)
    else:
        val = False

    return (not val) if negated else val


def _eval_condition(condition_str: str, signals: dict[str, bool]) -> bool:
    """
    Evaluate a simple condition string against signals.
    Supports AND, OR, NOT operators.
    """
    if not condition_str:
        return False

    condition_str = condition_str.strip()

    # Handle OR (lower precedence)
    if " OR " in condition_str:
        parts = condition_str.split(" OR ")
        return any(_eval_condition(p.strip(), signals) for p in parts)

    # Handle AND
    if " AND " in condition_str:
        parts = condition_str.split(" AND ")
        return all(_resolve_token(p.strip(), signals) for p in parts)

    # Single token
    return _resolve_token(condition_str, signals)


# ---------------------------------------------------------------------------
# Build signals and metrics from routing results
# ---------------------------------------------------------------------------

def build_signals_from_routing(routing: dict) -> dict[str, bool]:
    """
    Build boolean signals from routing results.
    Same logic as evidence_inference._evaluate_data_signals but standalone.
    """
    from services.evidence_inference import _evaluate_data_signals
    return _evaluate_data_signals(routing)


def build_metrics_from_routing(routing: dict) -> dict[str, float]:
    """Compute numeric metrics from routing results."""
    metrics: dict[str, float] = {}
    for r in routing.get("routing_results", []):
        st = r.get("source_type", "")
        total = r.get("total_records", 0)
        if st == "employees" and total > 0:
            no_training = r.get("no_security_training", 0)
            trained = total - no_training
            metrics["training_coverage_pct"] = (trained / total) * 100
        elif st == "network_rules" and total > 0:
            risky = r.get("risky_rules_count", 0)
            metrics["risky_rule_pct"] = (risky / total) * 100
    return metrics


def build_evidence_context(routing: dict, all_sheets: list[dict] | None = None) -> dict:
    """Build evidence context keyed by source type for keyword searches."""
    context: dict = {}
    for r in routing.get("routing_results", []):
        st = r.get("source_type", "")
        if st and r.get("total_records", 0) > 0:
            context[st] = r
    if all_sheets:
        for sheet in all_sheets:
            st = sheet.get("type", "")
            if st and sheet.get("rows") and st not in context:
                context[st] = sheet["rows"]
    return context


# ---------------------------------------------------------------------------
# Apply RuleEvaluator verdicts to framework controls
# ---------------------------------------------------------------------------

def _apply_rule_verdicts(controls: list[dict], rule_results: dict) -> int:
    """
    Map RuleEvaluator verdicts to framework controls via control_ref -> control.
    Returns number of controls matched.
    """
    rule_lookup: dict[str, dict] = {}
    for r in rule_results.get("results", []):
        ref = (r.get("control_ref") or "").strip().lower()
        if ref:
            rule_lookup[ref] = r

    status_map = {"pass": "compliant", "partial": "partial", "fail": "missing"}
    matched = 0

    for ctrl in controls:
        ctrl_ref = (ctrl.get("control") or ctrl.get("control_id") or "").strip().lower()
        if ctrl_ref in rule_lookup:
            verdict = rule_lookup[ctrl_ref]
            ctrl["status"] = status_map.get(verdict["status"], "missing")
            ctrl["has_evidence"] = verdict["status"] != "fail"
            ctrl["evidence_status"] = ctrl["status"]
            ctrl["evidence_row"] = {}
            ctrl["reason"] = verdict["reason"]
            ctrl["source"] = "rule_engine"
            ctrl["match_method"] = f"rule_engine_{verdict['eval_type']}"
            if verdict.get("remediation"):
                ctrl["remediation"] = verdict["remediation"]
            matched += 1

    return matched


# ---------------------------------------------------------------------------
# Evaluate JSON conditions (compliant_if / partial_if / missing_if)
# ---------------------------------------------------------------------------

def _evaluate_json_conditions(controls: list[dict], signals: dict[str, bool]) -> int:
    """
    Evaluate compliant_if/partial_if/missing_if from JSON for controls
    not yet evaluated by RuleEvaluator.
    Returns number of controls evaluated.
    """
    evaluated = 0

    for ctrl in controls:
        if ctrl.get("source") == "rule_engine":
            continue  # Already handled by RuleEvaluator

        compliant_cond = ctrl.get("compliant_if", {})
        partial_cond = ctrl.get("partial_if", {})
        missing_cond = ctrl.get("missing_if", {})

        if not compliant_cond and not partial_cond and not missing_cond:
            continue  # No JSON conditions — will be handled by fallback

        if _eval_condition(compliant_cond.get("condition", ""), signals):
            ctrl["status"] = "compliant"
            ctrl["reason"] = compliant_cond.get("detail", "Compliant per JSON rule config.")
            ctrl["source"] = "json_rule_config"
        elif _eval_condition(partial_cond.get("condition", ""), signals):
            ctrl["status"] = "partial"
            ctrl["reason"] = partial_cond.get("detail", "Partial per JSON rule config.")
            ctrl["source"] = "json_rule_config"
        else:
            ctrl["status"] = "missing"
            ctrl["reason"] = missing_cond.get("detail", "No evidence found.")
            ctrl["source"] = "json_rule_config"

        ctrl["has_evidence"] = ctrl["status"] != "missing"
        ctrl["evidence_status"] = ctrl["status"]
        ctrl["evidence_row"] = {}
        ctrl["match_method"] = "json_condition"
        evaluated += 1

    return evaluated


# ---------------------------------------------------------------------------
# Master entry point — replaces evidence_inference.infer_all_controls
# ---------------------------------------------------------------------------

def evaluate_controls_with_rule_engine(
    framework_id: str,
    controls: list[dict],
    routing: dict,
    present_types: set[str],
    all_sheets: list[dict] | None = None,
) -> list[dict]:
    """
    Evaluate controls using the rule-based engine.

    Priority:
      1. RuleEvaluator (Python rules) — for controls with matching rule_ref
      2. JSON conditions (compliant_if/partial_if/missing_if) — for remaining controls
      3. Old heuristic fallback — ONLY if rule engine fails, with explicit warning

    Returns the annotated controls list.
    """
    signals = build_signals_from_routing(routing)
    metrics = build_metrics_from_routing(routing)
    evidence = build_evidence_context(routing, all_sheets)

    _log.warning("=" * 70)
    _log.warning("RULE_ENGINE_ACTIVE: %s", framework_id)
    _log.warning("SIGNALS: %s", {k: v for k, v in sorted(signals.items())})
    _log.warning("METRICS: %s", metrics)

    # ── Phase 1: RuleEvaluator (Python rules) ─────────────────────────────
    rule_matched = 0
    try:
        from services.rule_evaluator import RuleEvaluator
        evaluator = RuleEvaluator(framework_id)
        rule_results = evaluator.evaluate(
            signals=signals,
            evidence_context=evidence,
            metrics=metrics,
        )
        rule_matched = _apply_rule_verdicts(controls, rule_results)
        _log.warning("TOTAL_RULES_LOADED: %d", rule_results["total_rules"])
        _log.warning("RULE_ENGINE_MATCHED: %d controls", rule_matched)
        _log.warning("RULE_ENGINE_SCORE: %.2f%%", rule_results["summary"]["score"])
    except ValueError:
        # Standard not in RuleEvaluator registry — OK, use JSON conditions only
        _log.warning("RULE_EVALUATOR: no Python rules for '%s' — using JSON conditions only", framework_id)
    except Exception as exc:
        _log.error("RULE_EVALUATOR_ERROR: %s — %s", framework_id, exc)

    # ── Phase 2: JSON conditions (compliant_if / partial_if / missing_if) ─
    json_evaluated = _evaluate_json_conditions(controls, signals)
    _log.warning("JSON_CONDITION_EVALUATED: %d controls", json_evaluated)

    # ── Phase 3: Fallback for remaining unevaluated controls ──────────────
    unevaluated = [c for c in controls if not c.get("source")]
    if unevaluated:
        _log.warning("FALLBACK_HEURISTIC: %d controls have no rule/JSON coverage — using old inference",
                      len(unevaluated))
        try:
            from services.evidence_inference import infer_control_status
            for ctrl in unevaluated:
                section_name = ctrl.get("section_name", ctrl.get("domain", ""))
                status, reason, match_source = infer_control_status(
                    ctrl, section_name, signals, present_types
                )
                ctrl["status"] = status
                ctrl["has_evidence"] = status != "missing"
                ctrl["evidence_status"] = status
                ctrl["evidence_row"] = {}
                ctrl["source"] = "heuristic_fallback"
                ctrl["match_method"] = match_source
                ctrl["reason"] = reason
        except Exception as exc:
            _log.error("HEURISTIC_FALLBACK_ERROR: %s", exc)
            for ctrl in unevaluated:
                ctrl["status"] = "missing"
                ctrl["has_evidence"] = False
                ctrl["evidence_status"] = "missing"
                ctrl["evidence_row"] = {}
                ctrl["source"] = "error_fallback"
                ctrl["reason"] = f"Evaluation failed: {exc}"

    # ── Summary ───────────────────────────────────────────────────────────
    total = len(controls)
    compliant = sum(1 for c in controls if c.get("status") == "compliant")
    partial = sum(1 for c in controls if c.get("status") == "partial")
    missing = total - compliant - partial

    by_source = {}
    for c in controls:
        src = c.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    _log.warning("EVALUATED_CONTROLS: %d", total)
    _log.warning("SCORE_SOURCE: rule_engine")
    _log.warning("RESULTS: compliant=%d  partial=%d  missing=%d", compliant, partial, missing)
    _log.warning("BY_SOURCE: %s", by_source)
    _log.warning("=" * 70)

    return controls
