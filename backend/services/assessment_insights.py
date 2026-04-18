"""
Assessment Insights Service.

Generates human-readable, rule-based insights from computed assessment metrics.
Every insight is grounded in actual data — no vague AI-generated text.
"""


def generate_insights(
    sections: list[dict],
    overall_score: float,
    severity_breakdown: dict,
    total_controls: int,
    compliant_controls: int,
    missing_controls: int,
) -> list[str]:
    """
    Generate a list of actionable insight strings from assessment results.

    Parameters
    ----------
    sections : list[dict]
        Annotated sections with compliance summaries.
    overall_score : float
        Overall compliance percentage.
    severity_breakdown : dict
        Severity-keyed dict with compliant/missing counts.
    total_controls : int
        Total number of controls.
    compliant_controls : int
        Number of compliant controls.
    missing_controls : int
        Number of missing controls.

    Returns
    -------
    list[str]
        Ordered list of concise, grounded insight statements.
    """
    insights: list[str] = []

    # ── Overall compliance level ──────────────────────────────────────────
    if overall_score == 100:
        insights.append("Full compliance achieved — all controls have mapped evidence.")
    elif overall_score >= 75:
        insights.append(
            f"Strong compliance posture at {overall_score}% — "
            f"{missing_controls} control(s) still require evidence."
        )
    elif overall_score >= 50:
        insights.append(
            f"Moderate compliance at {overall_score}% — "
            f"{missing_controls} of {total_controls} controls are missing evidence."
        )
    elif overall_score > 0:
        insights.append(
            f"Low compliance at {overall_score}% — "
            f"{missing_controls} of {total_controls} controls lack evidence. Immediate action recommended."
        )
    else:
        insights.append(
            "No evidence has been mapped to any control. "
            "Upload assessment evidence to begin compliance scoring."
        )

    # ── High-severity gaps ────────────────────────────────────────────────
    high = severity_breakdown.get("high", {})
    high_missing = high.get("missing", 0)
    high_total = high.get("total", 0)

    if high_missing > 0:
        # Identify which sections contain high-severity gaps
        sections_with_high_gaps = []
        for s in sections:
            high_missing_in_section = sum(
                1 for c in s.get("controls", [])
                if c.get("status") == "missing"
                and (c.get("severity") or "").lower() == "high"
            )
            if high_missing_in_section > 0:
                sections_with_high_gaps.append(
                    f"{s['section_key']} {s['section_name']} ({high_missing_in_section})"
                )

        insights.append(
            f"{high_missing} of {high_total} high-severity controls are missing evidence: "
            f"{', '.join(sections_with_high_gaps)}."
        )
    elif high_total > 0:
        insights.append(
            f"All {high_total} high-severity controls have mapped evidence."
        )

    # ── Specific missing high-severity controls ───────────────────────────
    for section in sections:
        for ctrl in section.get("controls", []):
            if (
                ctrl.get("status") == "missing"
                and (ctrl.get("severity") or "").lower() == "high"
            ):
                insights.append(
                    f"No evidence found for {ctrl.get('control', '')} "
                    f"{ctrl.get('name', '')} (high severity, {section['section_key']})."
                )

    # ── Best / worst sections ─────────────────────────────────────────────
    scored_sections = [
        s for s in sections
        if s.get("controls_count", 0) > 0
    ]

    if len(scored_sections) >= 2:
        best = max(scored_sections, key=lambda s: s.get("compliance_score", 0))
        worst = min(scored_sections, key=lambda s: s.get("compliance_score", 0))

        if best["compliance_score"] != worst["compliance_score"]:
            insights.append(
                f"{best['section_key']} {best['section_name']} has the highest compliance "
                f"at {best['compliance_score']}%."
            )
            insights.append(
                f"{worst['section_key']} {worst['section_name']} has the lowest compliance "
                f"at {worst['compliance_score']}% and should be prioritized."
            )

    # ── Largest gap section ───────────────────────────────────────────────
    if scored_sections:
        most_missing = max(scored_sections, key=lambda s: s.get("missing_controls", 0))
        if most_missing.get("missing_controls", 0) > 0:
            insights.append(
                f"{most_missing['section_key']} {most_missing['section_name']} "
                f"contains the largest number of missing controls "
                f"({most_missing['missing_controls']})."
            )

    # ── Medium / low severity notes ───────────────────────────────────────
    medium = severity_breakdown.get("medium", {})
    medium_missing = medium.get("missing", 0)
    if medium_missing > 0:
        insights.append(
            f"{medium_missing} medium-severity controls are still missing evidence."
        )

    low = severity_breakdown.get("low", {})
    low_missing = low.get("missing", 0)
    if low_missing > 0:
        insights.append(
            f"{low_missing} low-severity controls are missing evidence — "
            f"low priority but should be addressed for full compliance."
        )

    return insights
