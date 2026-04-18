"""
Control Mapping Service.

Maps uploaded Excel evidence rows to ISO framework controls.
Supports matching by rule_id, control, or required_evidence fields.
"""


def map_evidence_to_controls(
    uploaded_rows: list[dict],
    framework_sections: list[dict],
) -> dict:
    """
    Map uploaded assessment rows to framework controls.

    Attempts matching each uploaded row against each control using:
      1. rule_id  (exact, case-insensitive)
      2. control  (exact, case-insensitive)
      3. control_id from Excel → rule_id or control in framework

    Parameters
    ----------
    uploaded_rows : list[dict]
        Parsed rows from an uploaded Excel file.
    framework_sections : list[dict]
        Sections from the framework loader, each containing a "controls" list.

    Returns
    -------
    dict
        - mapped_controls: list of controls with matched evidence
        - unmapped_controls: list of controls with no match
        - unmatched_rows: list of uploaded rows that could not be matched
        - mapped_count: int
        - unmapped_count: int
    """
    # Build lookup indexes from framework controls
    controls_by_rule_id: dict[str, dict] = {}
    controls_by_control: dict[str, dict] = {}
    controls_by_evidence: dict[str, dict] = {}
    all_controls: list[dict] = []

    for section in framework_sections:
        section_key = section.get("section_key", "")
        section_name = section.get("section_name", "")
        for ctrl in section.get("controls", []):
            ctrl_copy = {**ctrl, "section_key": section_key, "section_name": section_name}
            all_controls.append(ctrl_copy)

            rid = (ctrl.get("rule_id") or "").strip().lower()
            cid = (ctrl.get("control") or "").strip().lower()
            eid = (ctrl.get("required_evidence") or "").strip().lower()

            if rid:
                controls_by_rule_id[rid] = ctrl_copy
            if cid:
                controls_by_control[cid] = ctrl_copy
            if eid:
                controls_by_evidence[eid] = ctrl_copy

    # Track which controls got matched
    matched_control_ids: set[str] = set()
    mapped_controls: list[dict] = []
    unmatched_rows: list[dict] = []

    for row in uploaded_rows:
        # Candidate keys from the uploaded row
        row_control_id = (row.get("control_id") or "").strip().lower()
        row_rule_id = (row.get("rule_id") or "").strip().lower()
        row_evidence = (row.get("required_evidence") or "").strip().lower()

        matched_ctrl = None

        # Priority 1: exact rule_id match
        if row_rule_id and row_rule_id in controls_by_rule_id:
            matched_ctrl = controls_by_rule_id[row_rule_id]
        # Priority 2: control_id → rule_id
        elif row_control_id and row_control_id in controls_by_rule_id:
            matched_ctrl = controls_by_rule_id[row_control_id]
        # Priority 3: control_id → control field
        elif row_control_id and row_control_id in controls_by_control:
            matched_ctrl = controls_by_control[row_control_id]
        # Priority 4: required_evidence match
        elif row_evidence and row_evidence in controls_by_evidence:
            matched_ctrl = controls_by_evidence[row_evidence]

        if matched_ctrl:
            ctrl_id = matched_ctrl.get("rule_id", "")
            if ctrl_id not in matched_control_ids:
                matched_control_ids.add(ctrl_id)
                mapped_controls.append({
                    **matched_ctrl,
                    "evidence_row": row,
                    "evidence_status": row.get("status", ""),
                })
        else:
            unmatched_rows.append(row)

    # Build unmapped controls list
    unmapped_controls = [
        ctrl for ctrl in all_controls
        if (ctrl.get("rule_id") or "").strip().lower() not in matched_control_ids
    ]

    return {
        "mapped_controls": mapped_controls,
        "unmapped_controls": unmapped_controls,
        "unmatched_rows": unmatched_rows,
        "mapped_count": len(mapped_controls),
        "unmapped_count": len(unmapped_controls),
    }
