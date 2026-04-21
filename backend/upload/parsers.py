"""
File parsers for uploaded content.
Each parser returns a structured dict or raises HTTPException on malformed input.
"""

import io
import json

from fastapi import HTTPException

from upload.header_normalizer import normalize_headers
from upload.sheet_classifier import classify_sheet, normalize_columns_for_type

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

try:
    import openpyxl
except ImportError:
    openpyxl = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Excel parser — Assessment mode
# ---------------------------------------------------------------------------

# Minimum canonical columns needed to extract useful data.
# We only need ONE of these to consider the file usable.
_MINIMUM_USEFUL_COLUMNS = {"control_id", "control_name", "status"}


def parse_excel(contents: bytes, filename: str) -> dict:
    """
    Parse an Excel workbook into a list-of-dicts with smart normalization.

    Pipeline:
      1. Load workbook
      2. Normalize headers via alias map (policy_name → control_name, etc.)
      3. Skip fully empty rows
      4. Trim all cell values
      5. Accept rows that have at least a control_id OR control_name

    Returns
    -------
    dict  with keys: rows, headers, total_rows, imported_rows, skipped_rows, errors
    """
    if openpyxl is None:
        raise HTTPException(status_code=500, detail="openpyxl is not installed.")

    try:
        wb = openpyxl.load_workbook(io.BytesIO(contents), read_only=True, data_only=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot read Excel file: {exc}")

    ws = wb.active
    if ws is None:
        raise HTTPException(status_code=400, detail="Workbook has no active sheet.")

    raw_rows = list(ws.iter_rows(values_only=True))
    if len(raw_rows) < 2:
        raise HTTPException(
            status_code=400,
            detail="Excel file must contain a header row and at least one data row.",
        )

    # ── 1. Normalize headers ─────────────────────────────────────────────
    raw_headers = raw_rows[0]
    headers = normalize_headers(raw_headers)

    # Check that at least one useful column was resolved
    found_useful = _MINIMUM_USEFUL_COLUMNS & set(headers)
    if not found_useful:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Aegis.One Mapping Error: We couldn't find your control columns. "
                f"Please ensure your Excel has columns like (ID, Policy Name, or Status). "
                f"Found these headers: {', '.join(h for h in headers if h)}"
            ),
        )

    # ── 2. Parse rows ────────────────────────────────────────────────────
    imported: list[dict] = []
    skipped = 0
    errors: list[str] = []

    for row_idx, row in enumerate(raw_rows[1:], start=2):
        # Skip completely empty rows
        if all(cell is None or str(cell).strip() == "" for cell in row):
            skipped += 1
            continue

        entry: dict = {}
        for col_idx, header in enumerate(headers):
            if not header:
                continue
            val = row[col_idx] if col_idx < len(row) else None
            entry[header] = str(val).strip() if val is not None else ""

        # Accept row if it has at least control_id or control_name
        has_id = bool(entry.get("control_id"))
        has_name = bool(entry.get("control_name"))

        if not has_id and not has_name:
            errors.append(f"Row {row_idx}: no control_id or control_name found — skipped.")
            skipped += 1
            continue

        imported.append(entry)

    wb.close()

    return {
        "rows": imported,
        "headers": [h for h in headers if h],
        "total_rows": len(raw_rows) - 1,
        "imported_rows": len(imported),
        "skipped_rows": skipped,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Configuration file parsers
# ---------------------------------------------------------------------------

def parse_json_config(contents: bytes, filename: str) -> dict:
    """Parse a JSON configuration file."""
    try:
        data = json.loads(contents.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Malformed JSON: {exc}")

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="JSON config must be a top-level object (not an array or scalar).",
        )

    return data


def parse_yaml_config(contents: bytes, filename: str) -> dict:
    """Parse a YAML / YML configuration file."""
    if yaml is None:
        raise HTTPException(status_code=500, detail="pyyaml is not installed.")

    try:
        data = yaml.safe_load(contents.decode("utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Malformed YAML: {exc}")

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="YAML config must be a top-level mapping (not a list or scalar).",
        )

    return data


def parse_env_config(contents: bytes, filename: str) -> dict:
    """Parse a .env file into key-value pairs."""
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Cannot decode .env file: {exc}")

    data: dict[str, str] = {}
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue  # silently skip malformed lines
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            data[key] = value

    if not data:
        raise HTTPException(status_code=400, detail=".env file contains no valid key=value pairs.")

    return data


def parse_config_file(contents: bytes, filename: str) -> tuple[dict, str]:
    """
    Dispatch to the correct parser based on extension.

    Returns (parsed_dict, detected_type_label).
    """
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if ext == ".json":
        return parse_json_config(contents, filename), "json"
    elif ext in {".yaml", ".yml"}:
        return parse_yaml_config(contents, filename), "yaml"
    elif ext == ".env":
        return parse_env_config(contents, filename), "env"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported config file type: {ext}")


# ---------------------------------------------------------------------------
# Multi-sheet Excel parser — Assessment mode
# ---------------------------------------------------------------------------

def parse_all_sheets(contents: bytes, filename: str) -> list[dict]:
    """
    Parse every sheet in an Excel workbook into a list of sheet dicts.

    Each element contains:
        name               : sheet name as it appears in the workbook
        type               : classified sheet type (assets / controls / vendors / …)
        row_count          : number of non-empty data rows
        headers            : raw header strings
        normalized_headers : canonical column names after alias mapping
        rows               : list of row dicts keyed by canonical column names

    Raises HTTPException on unreadable workbooks.
    """
    if openpyxl is None:
        raise HTTPException(status_code=500, detail="openpyxl is not installed.")

    try:
        wb = openpyxl.load_workbook(io.BytesIO(contents), read_only=True, data_only=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot read Excel file: {exc}")

    result: list[dict] = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        raw_rows = list(ws.iter_rows(values_only=True))

        if not raw_rows:
            # Empty sheet — include it so the caller can see all sheet names
            result.append({
                "name": sheet_name,
                "type": "unknown",
                "row_count": 0,
                "headers": [],
                "normalized_headers": [],
                "rows": [],
            })
            continue

        raw_headers = raw_rows[0]
        headers = [str(h).strip() if h is not None else "" for h in raw_headers]

        # Classify the sheet using name + headers
        sheet_type = classify_sheet(sheet_name, headers)

        # Normalize column names for the detected type
        normalized_headers = normalize_columns_for_type(headers, sheet_type)

        # Parse data rows
        rows: list[dict] = []
        for row in raw_rows[1:]:
            if all(cell is None or str(cell).strip() == "" for cell in row):
                continue  # skip fully empty rows
            entry: dict = {}
            for col_idx, canonical in enumerate(normalized_headers):
                if not canonical:
                    continue
                val = row[col_idx] if col_idx < len(row) else None
                entry[canonical] = str(val).strip() if val is not None else ""
            rows.append(entry)

        result.append({
            "name": sheet_name,
            "type": sheet_type,
            "row_count": len(rows),
            "headers": [h for h in headers if h],
            "normalized_headers": normalized_headers,
            "rows": rows,
        })

    wb.close()
    return result


# Backward-compat alias
parse_excel_multisheet = parse_all_sheets
