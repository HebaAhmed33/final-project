"""
Upload processors — business-logic hooks for Assessment and Configuration modes.

Each processor orchestrates: validate → parse → persist → trigger workflow.
Clean hooks are provided so future automation is easy to plug in.
"""

import os
import sys
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from upload.validators import validate_assessment_upload, validate_config_upload
from upload.parsers import parse_all_sheets, parse_config_file
from upload.sheet_router import route_sheets
from upload.storage import save_assessment_upload, save_config_upload


# ---------------------------------------------------------------------------
# Workflow hooks (extend later with real automation)
# ---------------------------------------------------------------------------

def _on_assessment_imported(record: dict) -> None:
    """
    Post-import hook for assessment uploads.

    Triggers the framework-aware assessment builder for ANY selected framework.
    Uses the routing result (all sheet types) + controls rows (from controls sheet).
    Result is stored in the record for later retrieval.
    """
    framework = (record.get("framework") or "").strip()
    if not framework:
        return  # No framework selected — skip assessment

    try:
        from services.framework_aware_builder import build_framework_aware_assessment

        routing = record.get("routed_analysis") or {}
        controls_rows = record.get("rows") or []  # controls-sheet rows only

        result = build_framework_aware_assessment(
            framework_id=framework,
            routing=routing,
            uploaded_controls=controls_rows,
            assessment_name=record.get("assessment_name", ""),
            scope=record.get("scope", ""),
            priority=record.get("priority", ""),
            notes=record.get("notes", ""),
            all_sheets=record.get("all_sheets", [])
        )
        record["framework_assessment"] = result
    except Exception as exc:
        import traceback
        traceback.print_exc()
        pass  # Non-critical — assessment can be re-run via /assess/{framework_id}


def _on_config_imported(record: dict) -> None:
    """
    Post-import hook for configuration uploads.

    Currently a no-op placeholder. Future implementation could:
    - trigger run_config_analysis with the parsed config
    - compare against config baselines
    - flag security misconfigurations
    """
    pass


# ---------------------------------------------------------------------------
# Assessment processor
# ---------------------------------------------------------------------------

async def process_assessment_upload(
    file: UploadFile,
    assessment_name: str = "",
    framework: str = "",
    scope: str = "",
    priority: str = "",
    notes: str = "",
) -> dict:
    """
    Full processing pipeline for an Assessment file upload.

    Flow (Step 3):
      1. Validate file (extension + size)
      2. Parse ALL sheets — metadata + normalized rows per sheet
      3. Route each sheet to its analysis path (assets / vendors / controls / …)
      4. Extract controls-sheet rows for backward-compat ISO 27001 hook
      5. Persist record
      6. Trigger ISO hook (if framework = iso27001 and controls rows exist)
      7. Return structured response with routing analysis and traceability
    """
    # 1. Validate
    contents = await validate_assessment_upload(file)

    # 2. Parse all sheets with normalized rows
    try:
        all_sheets = parse_all_sheets(contents, file.filename or "unknown.xlsx")
    except HTTPException:
        raise  # re-raise validation errors directly
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse workbook: {exc}")

    # 3. Route each sheet to the correct analysis path
    routing = route_sheets(all_sheets)

    # 4. Extract controls-sheet rows for backward-compat evidence hook
    #    Use the first non-empty controls sheet found.
    controls_sheet = next(
        (s for s in all_sheets if s["type"] == "controls" and s["row_count"] > 0),
        None,
    )
    controls_rows = controls_sheet["rows"] if controls_sheet else []

    # Aggregate stats across all sheets
    total_rows = sum(s["row_count"] for s in all_sheets)

    # Sheet detection summary (without raw rows — keep payload small)
    sheet_detection = {
        "total_sheets": len(all_sheets),
        "sheets": [
            {
                "name": s["name"],
                "type": s["type"],
                "row_count": s["row_count"],
                "headers": s["headers"],
                "normalized_headers": s["normalized_headers"],
            }
            for s in all_sheets
        ],
    }

    # 5. Build record
    record = {
        "id": str(uuid.uuid4()),
        "mode": "assessment",
        "file_name": file.filename,
        "assessment_name": assessment_name.strip(),
        "framework": framework.strip(),
        "scope": scope.strip(),
        "priority": priority.strip(),
        "notes": notes.strip(),
        "total_rows": total_rows,
        "imported_rows": total_rows,
        "skipped_rows": 0,
        # controls rows only — for ISO evidence hook backward compat
        "rows": controls_rows,
        "all_sheets": all_sheets, # pass the full sheet data temporarily so hook can use it
        "errors": [],
        "sheet_detection": sheet_detection,
        "routed_analysis": routing,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # 6. Workflow hook (generates assessment modules if framework is selected)
    _on_assessment_imported(record)

    # 7. Persist (remove all_sheets so it doesn't inflate JSON storage)
    if "all_sheets" in record:
        del record["all_sheets"]
    save_assessment_upload(record)

    framework_assessment = record.get("framework_assessment", {})

    # Bug 6 fix: compliance_score is always set at the root of framework_assessment
    # by build_framework_aware_assessment. The previous nested search was fragile
    # and could return None even when a valid score existed.
    compliance_score = framework_assessment.get("compliance_score", 0) if framework_assessment else 0

    # Compute risk summary from the risk_register sub-object
    risk_summary = {}
    rr = framework_assessment.get("risk_register", {}) if framework_assessment else {}
    if rr and rr.get("total_risks", 0) > 0:
        risk_summary = {
            "total_risks": rr.get("total_risks", 0),
            "high_risks":  rr.get("high_risks", 0),
        }

    # 8. Response
    return {
        "success": True,
        "message": "Assessment file processed and saved successfully.",
        "assessment_id": record["id"],
        "assessment_name": record["assessment_name"],
        "framework": record["framework"],
        "imported_count": total_rows,
        "detected_sheets": sheet_detection["total_sheets"],
        "compliance_score": compliance_score,
        "risk_summary": risk_summary,
        "generated_modules": list(framework_assessment.keys()) if framework_assessment else [],
        "framework_assessment": framework_assessment,
        "mode": "assessment",
        "file_name": record["file_name"],
        "total_rows": total_rows,
        "imported_rows": total_rows,
        "skipped_rows": 0,
        "metadata": {
            "id": record["id"],
            "assessment_name": record["assessment_name"],
            "framework": record["framework"],
            "scope": record["scope"],
            "priority": record["priority"],
            "notes": record["notes"],
        },
        "errors": [],
        "sheet_detection": sheet_detection,
        "routed_analysis": routing,
    }


# ---------------------------------------------------------------------------
# Configuration processor
# ---------------------------------------------------------------------------

async def process_config_upload(file: UploadFile) -> dict:
    """
    Full processing pipeline for a Configuration file upload.

    1. Validate file (extension + size)
    2. Parse by type (JSON / YAML / ENV)
    3. Persist to config_uploads.json
    4. Trigger workflow hook
    5. Return structured response
    """
    # 1. Validate
    contents = await validate_config_upload(file)

    # 2. Parse
    parsed_data, detected_type = parse_config_file(contents, file.filename or "unknown")

    top_level_keys = list(parsed_data.keys())

    # 3. Build record
    record = {
        "id": str(uuid.uuid4()),
        "mode": "configuration",
        "file_name": file.filename,
        "file_type": detected_type,
        "parsed_keys_count": len(top_level_keys),
        "top_level_keys": top_level_keys,
        "parsed_config": parsed_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # 4. Persist
    save_config_upload(record)

    # 5. Workflow hook
    _on_config_imported(record)

    # 6. Response
    return {
        "success": True,
        "message": "Configuration file processed and saved successfully.",
        "mode": "configuration",
        "file_name": record["file_name"],
        "file_type": record["file_type"],
        "parsed_keys_count": record["parsed_keys_count"],
        "top_level_keys": record["top_level_keys"],
        "errors": [],
    }
