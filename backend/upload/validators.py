"""
Upload validators.
Server-side validation for file uploads — never trust the frontend.
"""

from fastapi import UploadFile, HTTPException

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ASSESSMENT_EXTENSIONS = {".xlsx", ".xls"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".env", ".sh", ".conf", ".log", ".txt", ".fw"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_extension(filename: str) -> str:
    """Return the lowercased file extension (e.g. '.xlsx')."""
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


# ---------------------------------------------------------------------------
# Public validators
# ---------------------------------------------------------------------------

async def validate_upload(file: UploadFile, allowed_extensions: set[str]) -> bytes:
    """
    Read, validate size and extension, and return raw bytes.

    Raises HTTPException on any validation failure.
    """
    if file is None or file.filename is None:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = _get_extension(file.filename)
    if ext not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {allowed}",
        )

    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE_MB} MB.",
        )

    return contents


async def validate_assessment_upload(file: UploadFile) -> bytes:
    """Validate an assessment Excel upload."""
    return await validate_upload(file, ASSESSMENT_EXTENSIONS)


async def validate_config_upload(file: UploadFile) -> bytes:
    """Validate a configuration file upload."""
    return await validate_upload(file, CONFIG_EXTENSIONS)
