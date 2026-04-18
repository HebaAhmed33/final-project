"""
Upload storage helpers.
File-based JSON persistence for assessment and configuration uploads.
Follows the same pattern as isms_core/report_history_manager.py.
"""

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

_ASSESSMENTS_FILE = os.path.join(_DATA_DIR, "assessments.json")
_CONFIG_UPLOADS_FILE = os.path.join(_DATA_DIR, "config_uploads.json")


def _ensure_dir() -> None:
    os.makedirs(_DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Generic load/save
# ---------------------------------------------------------------------------

def _load(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(path: str, data: list[dict]) -> None:
    _ensure_dir()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Assessment storage
# ---------------------------------------------------------------------------

def save_assessment_upload(entry: dict) -> None:
    """Append an assessment upload record."""
    records = _load(_ASSESSMENTS_FILE)
    records.append(entry)
    _save(_ASSESSMENTS_FILE, records)


def get_assessment_uploads() -> list[dict]:
    """Return all assessment upload records."""
    return _load(_ASSESSMENTS_FILE)


def get_latest_assessment_evidence() -> list[dict] | None:
    """
    Return the parsed rows from the most recent assessment upload.

    Returns None if no uploads exist or the most recent has no rows.
    """
    records = _load(_ASSESSMENTS_FILE)
    if not records:
        return None
    latest = records[-1]
    rows = latest.get("rows")
    if not rows:
        return None
    return rows


def get_assessment_evidence_summary() -> dict | None:
    """
    Return a lightweight summary of the most recent uploaded evidence.

    Used by the frontend to detect whether evidence is available
    without loading the full row data.
    """
    records = _load(_ASSESSMENTS_FILE)
    if not records:
        return None
    latest = records[-1]
    rows = latest.get("rows", [])
    if not rows:
        return None
    return {
        "upload_id": latest.get("id", ""),
        "file_name": latest.get("file_name", ""),
        "framework": latest.get("framework", ""),
        "assessment_name": latest.get("assessment_name", ""),
        "row_count": len(rows),
        "uploaded_at": latest.get("created_at", ""),
    }


# ---------------------------------------------------------------------------
# Configuration storage
# ---------------------------------------------------------------------------

def save_config_upload(entry: dict) -> None:
    """Append a configuration upload record."""
    records = _load(_CONFIG_UPLOADS_FILE)
    records.append(entry)
    _save(_CONFIG_UPLOADS_FILE, records)


def get_config_uploads() -> list[dict]:
    """Return all configuration upload records."""
    return _load(_CONFIG_UPLOADS_FILE)
