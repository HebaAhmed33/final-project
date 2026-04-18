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
from upload.parsers import parse_excel, parse_config_file
from upload.storage import save_assessment_upload, save_config_upload


# ---------------------------------------------------------------------------
# Workflow hooks (extend later with real automation)
# ---------------------------------------------------------------------------

def _on_assessment_imported(record: dict) -> None:
    """
    Post-import hook for assessment uploads.

    When the framework is ISO 27001, automatically build a structured
    grouped assessment with evidence mapping.
    """
    fw = (record.get("framework") or "").strip().lower().replace(" ", "").replace("-", "")
    if fw in ("iso27001", "iso270012022"):
        try:
            from services.assessment_builder import build_assessment

            result = build_assessment(
                framework="iso27001",
                uploaded_rows=record.get("rows"),
                assessment_name=record.get("assessment_name", ""),
                scope=record.get("scope", ""),
                priority=record.get("priority", ""),
                notes=record.get("notes", ""),
            )
            record["iso27001_assessment"] = result
        except Exception:
            pass  # non-critical — assessment can be built later via /assess/iso27001


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

    1. Validate file (extension + size)
    2. Parse Excel (headers, rows, empty-row handling)
    3. Persist to assessments.json
    4. Trigger workflow hook
    5. Return structured response
    """
    # 1. Validate
    contents = await validate_assessment_upload(file)

    # 2. Parse
    parsed = parse_excel(contents, file.filename or "unknown.xlsx")

    # 3. Build record
    record = {
        "id": str(uuid.uuid4()),
        "mode": "assessment",
        "file_name": file.filename,
        "assessment_name": assessment_name.strip(),
        "framework": framework.strip(),
        "scope": scope.strip(),
        "priority": priority.strip(),
        "notes": notes.strip(),
        "total_rows": parsed["total_rows"],
        "imported_rows": parsed["imported_rows"],
        "skipped_rows": parsed["skipped_rows"],
        "rows": parsed["rows"],
        "errors": parsed["errors"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # 4. Persist
    save_assessment_upload(record)

    # 5. Workflow hook
    _on_assessment_imported(record)

    # 6. Response (exclude raw rows to keep payload reasonable)
    return {
        "success": True,
        "message": "Assessment file processed and saved successfully.",
        "mode": "assessment",
        "file_name": record["file_name"],
        "total_rows": record["total_rows"],
        "imported_rows": record["imported_rows"],
        "skipped_rows": record["skipped_rows"],
        "metadata": {
            "id": record["id"],
            "assessment_name": record["assessment_name"],
            "framework": record["framework"],
            "scope": record["scope"],
            "priority": record["priority"],
            "notes": record["notes"],
        },
        "errors": record["errors"],
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
