"""
Framework Loader Service.

Dynamically loads framework control libraries from structured JSON files
stored under ``backend/standards/<framework_id>/``.

Currently supports ISO 27001 with grouped sections (A6, A7, A8).
Designed to be extensible — to add a new framework, just:
  1. Create ``backend/standards/<id>/`` with section JSON files
  2. Add the section registry + loader function
  3. Register the framework key in _FRAMEWORK_REGISTRY
"""

import json
import os
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STANDARDS_DIR = os.path.join(_BACKEND_DIR, "standards")

# ---------------------------------------------------------------------------
# ISO 27001 section registry
# ---------------------------------------------------------------------------
# Ordered list — controls the display order in responses.
# To add A5 in the future, just prepend an entry here.

ISO27001_SECTIONS = [
    {
        "section_key": "A6",
        "section_name": "People Controls",
        "file_name": "A6_people_controls.json",
    },
    {
        "section_key": "A7",
        "section_name": "Physical Controls",
        "file_name": "A7_physical_controls.json",
    },
    {
        "section_key": "A8",
        "section_name": "Technological Controls",
        "file_name": "A8_technological_controls.json",
    },
]

# Map of supported frameworks → their internal loader key
_FRAMEWORK_REGISTRY: dict[str, str] = {
    "iso27001": "iso27001",
    "iso 27001": "iso27001",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_framework_dir(framework_id: str) -> str:
    """Return the absolute path to a framework's standards directory."""
    return os.path.join(_STANDARDS_DIR, framework_id)


def _read_json_safe(path: str) -> tuple[Optional[list], Optional[str]]:
    """
    Read a JSON file and return (data, error).

    Returns (list, None) on success or (None, error_message) on failure.
    """
    if not os.path.exists(path):
        return None, f"File not found: {os.path.basename(path)}"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            return None, f"Expected JSON array in {os.path.basename(path)}, got {type(data).__name__}"
        return data, None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, f"Malformed JSON in {os.path.basename(path)}: {exc}"


def _compute_severity_summary(controls: list[dict]) -> dict[str, int]:
    """Count controls by severity level."""
    summary: dict[str, int] = {}
    for ctrl in controls:
        sev = (ctrl.get("severity") or "unknown").lower()
        summary[sev] = summary.get(sev, 0) + 1
    return summary


# ---------------------------------------------------------------------------
# ISO 27001 loader
# ---------------------------------------------------------------------------

def load_iso27001_sections() -> dict:
    """
    Load all ISO 27001 grouped sections from disk.

    Reads from: ``backend/standards/iso27001/``

    Returns the full structured response with sections, controls, and metadata.
    Gracefully handles missing or malformed files per-section.
    """
    iso_dir = _get_framework_dir("iso27001")

    if not os.path.isdir(iso_dir):
        raise ValueError(
            f"ISO 27001 standards directory not found: {iso_dir}. "
            f"Expected directory at backend/standards/iso27001/"
        )

    sections = []
    total_controls = 0
    all_controls_flat: list[dict] = []
    errors: list[str] = []

    for section_def in ISO27001_SECTIONS:
        file_path = os.path.join(iso_dir, section_def["file_name"])
        controls, err = _read_json_safe(file_path)

        if err:
            errors.append(err)
            sections.append({
                "section_key": section_def["section_key"],
                "section_name": section_def["section_name"],
                "controls": [],
                "controls_count": 0,
                "error": err,
            })
            continue

        total_controls += len(controls)
        all_controls_flat.extend(controls)

        sections.append({
            "section_key": section_def["section_key"],
            "section_name": section_def["section_name"],
            "controls": controls,
            "controls_count": len(controls),
        })

    return {
        "framework": "ISO27001",
        "total_sections": len(sections),
        "total_controls": total_controls,
        "severity_summary": _compute_severity_summary(all_controls_flat),
        "sections": sections,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Generic framework dispatcher
# ---------------------------------------------------------------------------

def load_framework(framework: str) -> dict:
    """
    Load a framework's control library by name.

    Parameters
    ----------
    framework : str
        Framework identifier (e.g. "ISO 27001", "iso27001").

    Returns
    -------
    dict
        Structured framework payload with sections and controls.

    Raises
    ------
    ValueError
        If the framework is not supported or directory is missing.
    """
    key = framework.strip().lower().replace("-", "").replace("_", " ")
    resolved = _FRAMEWORK_REGISTRY.get(key)

    if resolved == "iso27001":
        return load_iso27001_sections()

    raise ValueError(
        f"Unsupported framework: '{framework}'. "
        f"Supported: {', '.join(sorted(set(_FRAMEWORK_REGISTRY.values())))}"
    )


def get_supported_frameworks() -> list[str]:
    """Return list of supported framework identifiers."""
    return sorted(set(_FRAMEWORK_REGISTRY.values()))
