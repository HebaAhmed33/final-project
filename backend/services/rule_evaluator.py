"""
Rule-Based Evaluator Service — Core Engine.

Loads rule configurations by selected standard and evaluates them
against uploaded organizational data (signals, evidence, metrics).

╔══════════════════════════════════════════════════════════════════╗
║  PHASE 1 — STANDALONE ENGINE                                    ║
║  This module is NOT connected to the scoring pipeline yet.       ║
║  It can be invoked independently for dry-run evaluation.         ║
╚══════════════════════════════════════════════════════════════════╝

Usage (dry run):
    from services.rule_evaluator import RuleEvaluator

    evaluator = RuleEvaluator("iso27001")
    results   = evaluator.evaluate(signals, evidence_context)
"""

from __future__ import annotations

import logging
from typing import Any

# ── Rule imports ──────────────────────────────────────────────────────────
from rules.iso27001_rules import ISO27001_RULES
from rules.hipaa_rules import HIPAA_RULES
from rules.pci_dss_rules import PCI_DSS_RULES
from rules.sama_rules import SAMA_RULES

_log = logging.getLogger(__name__)

# ── Registry ──────────────────────────────────────────────────────────────
# Maps standard id → (rule list, human label)

_RULE_REGISTRY: dict[str, tuple[list[dict], str]] = {
    "iso27001": (ISO27001_RULES, "ISO 27001"),
    "hipaa":    (HIPAA_RULES,    "HIPAA"),
    "pci_dss":  (PCI_DSS_RULES,  "PCI DSS"),
    "sama":     (SAMA_RULES,     "SAMA CSF"),
}


def get_available_standards() -> list[dict]:
    """Return metadata for every registered standard."""
    return [
        {"id": sid, "label": label, "rule_count": len(rules)}
        for sid, (rules, label) in _RULE_REGISTRY.items()
    ]


# ── Evaluation helpers ────────────────────────────────────────────────────

def _compare(operator: str, actual: float, expected: float) -> bool:
    """Apply a threshold comparison operator."""
    ops = {
        "gte": actual >= expected,
        "lte": actual <= expected,
        "gt":  actual > expected,
        "lt":  actual < expected,
        "eq":  actual == expected,
    }
    return ops.get(operator, False)


def _eval_evidence_keyword(
    config: dict,
    evidence_context: dict[str, Any],
) -> tuple[str, str]:
    """
    Check if any keyword appears in the evidence data for the
    specified source types.

    Returns (status, reason).
    """
    keywords = [kw.lower() for kw in config.get("keywords", [])]
    sources = config.get("evidence_sources", [])
    match_mode = config.get("match_mode", "any")

    if not keywords:
        return "missing", "No keywords configured for this rule."

    # Collect text from evidence sources
    hits: list[str] = []
    for src in sources:
        src_data = evidence_context.get(src)
        if src_data is None:
            continue

        # src_data can be:
        #   - a list of dicts (rows from a sheet)
        #   - a dict (single result)
        #   - a string (raw text)
        text_blob = ""
        if isinstance(src_data, list):
            text_blob = " ".join(
                " ".join(str(v) for v in row.values()) if isinstance(row, dict) else str(row)
                for row in src_data
            ).lower()
        elif isinstance(src_data, dict):
            text_blob = " ".join(str(v) for v in src_data.values()).lower()
        elif isinstance(src_data, str):
            text_blob = src_data.lower()

        for kw in keywords:
            if kw in text_blob:
                hits.append(kw)

    unique_hits = list(set(hits))

    if match_mode == "all" and len(unique_hits) >= len(keywords):
        return "pass", f"All keywords matched: {', '.join(unique_hits)}."
    elif match_mode == "all" and unique_hits:
        return "partial", f"Partial keyword match ({len(unique_hits)}/{len(keywords)}): {', '.join(unique_hits)}."
    elif unique_hits:
        return "pass", f"Keyword evidence found: {', '.join(unique_hits)}."
    else:
        return "fail", f"No keyword evidence found. Expected: {', '.join(keywords)}."


def _eval_field_present(
    config: dict,
    evidence_context: dict[str, Any],
) -> tuple[str, str]:
    """
    Check if required fields exist in the evidence sources.
    Returns (status, reason).
    """
    required = config.get("required_fields", [])
    sources = config.get("evidence_sources", [])
    found: list[str] = []
    missing_fields: list[str] = []

    for src in sources:
        src_data = evidence_context.get(src)
        if not src_data:
            continue
        # Take first row if list
        sample = src_data[0] if isinstance(src_data, list) and src_data else src_data
        if isinstance(sample, dict):
            for field in required:
                if field in sample and sample[field]:
                    found.append(field)

    missing_fields = [f for f in required if f not in found]

    if not missing_fields:
        return "pass", f"All required fields present: {', '.join(required)}."
    elif found:
        return "partial", f"Fields found: {', '.join(found)}. Missing: {', '.join(missing_fields)}."
    else:
        return "fail", f"Required fields missing: {', '.join(required)}."


def _eval_threshold(
    config: dict,
    metrics: dict[str, float],
) -> tuple[str, str]:
    """
    Compare a computed metric against a threshold.
    Returns (status, reason).
    """
    metric_name = config.get("metric", "")
    operator = config.get("operator", "gte")
    expected = config.get("value", 0.0)

    actual = metrics.get(metric_name)
    if actual is None:
        return "fail", f"Metric '{metric_name}' not available in uploaded data."

    if _compare(operator, actual, expected):
        return "pass", f"{metric_name} = {actual:.1f} ({operator} {expected})."
    else:
        return "fail", f"{metric_name} = {actual:.1f} (required {operator} {expected})."


def _eval_boolean(
    config: dict,
    signals: dict[str, bool],
) -> tuple[str, str]:
    """
    Check a boolean signal.
    Returns (status, reason).
    """
    signal_name = config.get("signal", "")
    expected = config.get("expected", True)
    actual = signals.get(signal_name)

    if actual is None:
        return "fail", f"Signal '{signal_name}' not found in uploaded data."
    if actual == expected:
        return "pass", f"Signal '{signal_name}' = {actual} (expected {expected})."
    else:
        return "fail", f"Signal '{signal_name}' = {actual} (expected {expected})."


# ══════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════

class RuleEvaluator:
    """
    Configurable rule-based evaluator for a single compliance standard.

    Initialise with a standard id (e.g. "iso27001"), then call
    `.evaluate()` with data context to produce per-rule verdicts.

    This class is stateless after init — safe to reuse across requests.
    """

    def __init__(self, standard_id: str) -> None:
        entry = _RULE_REGISTRY.get(standard_id)
        if entry is None:
            raise ValueError(
                f"Unknown standard '{standard_id}'. "
                f"Available: {list(_RULE_REGISTRY.keys())}"
            )
        self.standard_id = standard_id
        self.rules, self.label = entry

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    # ──────────────────────────────────────────────────────────────────
    def evaluate(
        self,
        signals: dict[str, bool] | None = None,
        evidence_context: dict[str, Any] | None = None,
        metrics: dict[str, float] | None = None,
    ) -> dict:
        """
        Evaluate all rules for the loaded standard.

        Parameters
        ----------
        signals : dict[str, bool]
            Boolean signals produced by _evaluate_data_signals()
            (e.g. has_employee_records, has_network_rules, ...).

        evidence_context : dict[str, Any]
            Raw evidence data keyed by sheet/source type
            (e.g. {"governance": [...], "vendors": [...], ...}).

        metrics : dict[str, float]
            Computed numeric metrics
            (e.g. training_coverage_pct, risky_rule_pct, ...).

        Returns
        -------
        dict with:
            standard_id, label, total_rules,
            results (list[dict]), summary (dict).
        """
        signals = signals or {}
        evidence_context = evidence_context or {}
        metrics = metrics or {}

        results: list[dict] = []

        for rule in self.rules:
            eval_type = rule["eval_type"]
            config = rule["eval_config"]

            if eval_type == "evidence_keyword":
                status, reason = _eval_evidence_keyword(config, evidence_context)
            elif eval_type == "field_present":
                status, reason = _eval_field_present(config, evidence_context)
            elif eval_type == "threshold":
                status, reason = _eval_threshold(config, metrics)
            elif eval_type == "boolean":
                status, reason = _eval_boolean(config, signals)
            else:
                status, reason = "fail", f"Unknown eval_type '{eval_type}'."

            results.append({
                "rule_id":      rule["rule_id"],
                "control_ref":  rule.get("control_ref", ""),
                "name":         rule["name"],
                "domain":       rule.get("domain", ""),
                "severity":     rule["severity"],
                "eval_type":    eval_type,
                "status":       status,
                "reason":       reason,
                "remediation":  rule.get("remediation", ""),
            })

        # Summary
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "pass")
        partial = sum(1 for r in results if r["status"] == "partial")
        failed = total - passed - partial

        _log.info(
            "[RuleEvaluator] %s evaluation complete — "
            "pass=%d partial=%d fail=%d total=%d",
            self.label, passed, partial, failed, total,
        )

        return {
            "standard_id":  self.standard_id,
            "label":        self.label,
            "total_rules":  total,
            "results":      results,
            "summary": {
                "passed":  passed,
                "partial": partial,
                "failed":  failed,
                "score":   round(((passed + partial * 0.5) / total) * 100, 2) if total > 0 else 0.0,
            },
        }

    # ──────────────────────────────────────────────────────────────────
    def dry_run(self) -> dict:
        """
        Run the evaluator with empty data — useful for validation
        and for listing all rules without actual data.
        """
        return self.evaluate(signals={}, evidence_context={}, metrics={})
