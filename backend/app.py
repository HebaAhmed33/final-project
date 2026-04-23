"""
SmartISMS FastAPI Application.
Exposes the assessment and reporting pipelines as REST endpoints.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from integration.full_combined_runner import run_full_combined_analysis
from isms_core.report_history_manager import get_reports, save_report
from isms_core.rule_engine import evaluate
from config_analysis.config_input_mapper import map_config_input
from config_analysis.technical_findings_formatter import format_technical_findings
from config_analysis.technical_risk_engine import create_technical_risks
from reporting.report_export_service import export_company_latest_report_pdf
from news.news_service import fetch_news
from upload.processors import process_assessment_upload, process_config_upload
from upload.storage import (
    get_assessment_uploads, get_config_uploads,
    get_latest_assessment_evidence, get_assessment_evidence_summary,
)
from services.framework_loader import load_framework, get_supported_frameworks
from services.assessment_builder import build_assessment
from services.assessment_history import (
    save_assessment_run, get_assessment_history, prepare_export_payload,
)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class FullAnalysisRequest(BaseModel):
    raw_data: dict
    raw_config_data: dict
    standard_file: str
    config_standard_file: str


class CompanyInfo(BaseModel):
    id: str
    name: str
    organization_type: str
    sector: str = ""
    country: str = ""


class RunAndSaveRequest(BaseModel):
    company: CompanyInfo
    raw_data: dict
    raw_config_data: dict
    standard_file: str
    config_standard_file: str


class ExportReportRequest(BaseModel):
    company_id: str


class ConfigAnalysisRequest(BaseModel):
    raw_config_data: dict
    config_standard_file: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RequestAccessRequest(BaseModel):
    company_name: str
    email: str
    organization_type: str
    sector: str = ""
    notes: str = ""


# Hardcoded demo user
DEMO_USER = {
    "email": "demo@smartisms.com",
    "password": "demo123",
    "id": "U001",
    "company_id": "C001",
    "role": "admin",
}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="SmartISMS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check."""
    return {"message": "SmartISMS API running"}


@app.post("/login")
def login(request: LoginRequest):
    """Authenticate with hardcoded demo credentials."""
    if request.email == DEMO_USER["email"] and request.password == DEMO_USER["password"]:
        return {
            "success": True,
            "user": {
                "id": DEMO_USER["id"],
                "company_id": DEMO_USER["company_id"],
                "email": DEMO_USER["email"],
                "role": DEMO_USER["role"],
            },
        }
    return {"success": False, "message": "Invalid credentials"}


# ---------------------------------------------------------------------------
# Access-request persistence helpers
# ---------------------------------------------------------------------------

_ACCESS_REQUESTS_FILE = os.path.join(
    os.path.dirname(__file__), "data", "access_requests.json"
)


def _load_access_requests() -> list[dict]:
    """Read the access-requests JSON file, returning [] if missing."""
    if not os.path.exists(_ACCESS_REQUESTS_FILE):
        return []
    with open(_ACCESS_REQUESTS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_access_requests(requests: list[dict]) -> None:
    """Write the full list back to disk, creating the directory if needed."""
    os.makedirs(os.path.dirname(_ACCESS_REQUESTS_FILE), exist_ok=True)
    with open(_ACCESS_REQUESTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(requests, fh, indent=2, ensure_ascii=False)


@app.post("/request-access")
def request_access(request: RequestAccessRequest):
    """Persist a SaaS access request to local JSON storage."""
    entry = {
        "id": str(uuid.uuid4()),
        "company_name": request.company_name,
        "email": request.email,
        "organization_type": request.organization_type,
        "sector": request.sector,
        "notes": request.notes,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    all_requests = _load_access_requests()
    all_requests.append(entry)
    _save_access_requests(all_requests)
    return {"success": True, "message": "Request received. Our team will contact you shortly."}


@app.get("/access-requests")
def list_access_requests():
    """Return every access request on file."""
    return {"requests": _load_access_requests()}


@app.post("/run-full-analysis")
def run_full_analysis(request: FullAnalysisRequest):
    """Run the full combined analysis pipeline."""
    result = run_full_combined_analysis(
        raw_data=request.raw_data,
        raw_config_data=request.raw_config_data,
        standard_file=request.standard_file,
        config_standard_file=request.config_standard_file,
    )
    return result


@app.post("/run-and-save-assessment")
def run_and_save_assessment(request: RunAndSaveRequest):
    """Run the combined analysis pipeline and save the report."""
    combined_output = run_full_combined_analysis(
        raw_data=request.raw_data,
        raw_config_data=request.raw_config_data,
        standard_file=request.standard_file,
        config_standard_file=request.config_standard_file,
    )
    stored_report = {
        "company_id": request.company.id,
        "company_name": request.company.name,
        "organization_type": request.company.organization_type,
        "standard_file": request.standard_file,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assessment_output": combined_output["assessment"],
        "combined_output": combined_output,
    }
    save_report(request.company.id, stored_report)
    return stored_report


@app.get("/reports/{company_id}")
def get_company_reports(company_id: str):
    """Return all saved reports for a company."""
    reports = get_reports(company_id)
    return {"company_id": company_id, "total_reports": len(reports), "reports": reports}


@app.post("/export-latest-report")
def export_latest_report(request: ExportReportRequest):
    """Generate a PDF from the latest saved report for a company."""
    output_dir = os.path.join(os.path.dirname(__file__), "exports")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{request.company_id}_executive_report.pdf")

    result = export_company_latest_report_pdf(request.company_id, output_path)
    if result is None:
        return {"status": "error", "message": f"No report found for company '{request.company_id}'."}
    return {"status": "success", "output_path": result}


# ---------------------------------------------------------------------------
# Run: uvicorn backend.app:app --reload
# ---------------------------------------------------------------------------


@app.post("/run-config-analysis")
def run_config_analysis(request: ConfigAnalysisRequest):
    """Run config-only technical analysis."""
    normalized = map_config_input(request.raw_config_data)
    results = evaluate(normalized, request.config_standard_file)
    findings = format_technical_findings(results)
    risks = create_technical_risks(results)
    return {
        "summary": findings["summary"],
        "findings": findings["findings"],
        "risks": risks,
    }


@app.get("/news")
def get_news():
    """Return aggregated cybersecurity and GRC news articles."""
    return fetch_news()


# ---------------------------------------------------------------------------
# File Upload endpoints — Assessment & Configuration modes
# ---------------------------------------------------------------------------

@app.post("/upload/assessment")
async def upload_assessment(
    file: UploadFile = File(...),
    assessment_name: str = Form(""),
    framework: str = Form(""),
    scope: str = Form(""),
    priority: str = Form(""),
    notes: str = Form(""),
):
    """Upload an Excel file for assessment processing."""
    try:
        print(f"[DEBUG] UPLOAD ENDPOINT HIT - file={file.filename}")
        return await process_assessment_upload(
            file=file,
            assessment_name=assessment_name,
            framework=framework,
            scope=scope,
            priority=priority,
            notes=notes,
        )
    except HTTPException:
        raise  # Let FastAPI handle validation errors with proper status codes
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error during upload: {exc}")


@app.get("/upload/assessments")
def list_assessment_uploads():
    """Return all persisted assessment upload records."""
    return {"uploads": get_assessment_uploads()}


@app.post("/upload/configuration")
async def upload_configuration(
    file: UploadFile = File(...),
):
    """Upload a configuration file (JSON / YAML / ENV) for processing."""
    return await process_config_upload(file=file)


@app.get("/upload/configurations")
def list_config_uploads():
    """Return all persisted configuration upload records."""
    return {"uploads": get_config_uploads()}


# ---------------------------------------------------------------------------
# ISO 27001 Grouped Assessment endpoints
# ---------------------------------------------------------------------------

@app.get("/frameworks")
def list_frameworks():
    """Return all available assessment frameworks from the standards directory."""
    import glob

    standards_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standards")
    frameworks = []

    # Human-readable label mapping
    labels = {
        "iso27001": "ISO 27001",
        "nist": "NIST",
        "pci_dss": "PCI DSS",
        "hipaa": "HIPAA",
        "sama": "SAMA",
        "cis": "CIS",
    }

    # Detect grouped frameworks (directories like standards/iso27001/)
    if os.path.isdir(standards_dir):
        for entry in sorted(os.listdir(standards_dir)):
            full = os.path.join(standards_dir, entry)
            if os.path.isdir(full):
                frameworks.append({
                    "id": entry,
                    "label": labels.get(entry, entry.upper()),
                    "type": "enriched",
                })
            elif entry.endswith(".json") and entry not in ("config_baseline.json", "standard_profiles.json"):
                fid = entry.replace(".json", "")
                if fid not in [f["id"] for f in frameworks]:
                    frameworks.append({
                        "id": fid,
                        "label": labels.get(fid, fid.upper().replace("_", " ")),
                        "type": "legacy",
                    })

    return {"frameworks": frameworks}


@app.get("/frameworks/iso27001")
def get_iso27001_controls():
    """Return ISO 27001 controls grouped by section (A6, A7, A8)."""
    try:
        data = load_framework("iso27001")
        return {"success": True, **data}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class ISO27001AssessmentRequest(BaseModel):
    assessment_name: str = ""
    scope: str = ""
    priority: str = ""
    notes: str = ""
    uploaded_rows: list[dict] | None = None
    use_uploaded_evidence: bool = True


@app.post("/assess/iso27001")
def run_iso27001_assessment(request: ISO27001AssessmentRequest):
    """
    Build a structured ISO 27001 assessment with optional evidence mapping.

    Evidence resolution order:
      1. Rows passed directly in `uploaded_rows` (highest priority)
      2. Auto-loaded from the most recent assessment upload if `use_uploaded_evidence` is True
      3. None — baseline-only assessment
    """
    try:
        # Resolve evidence
        evidence_rows = request.uploaded_rows
        evidence_source = ""

        if evidence_rows:
            evidence_source = "direct_payload"
        elif request.use_uploaded_evidence:
            evidence_rows = get_latest_assessment_evidence()
            if evidence_rows:
                evidence_source = "latest_upload"

        result = build_assessment(
            framework="iso27001",
            uploaded_rows=evidence_rows,
            assessment_name=request.assessment_name,
            scope=request.scope,
            priority=request.priority,
            notes=request.notes,
        )

        # Tag the result with source info
        result["evidence_source"] = evidence_source
        result["evidence_backed"] = bool(evidence_rows)

        # Save to history
        save_assessment_run(result)

        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/assess/evidence-summary")
def get_evidence_summary():
    """Return a lightweight summary of the most recent uploaded evidence."""
    summary = get_assessment_evidence_summary()
    return {"has_evidence": summary is not None, "evidence": summary}


@app.get("/assess/history")
def get_history():
    """Return all assessment execution history records."""
    return {"history": get_assessment_history()}


@app.post("/assess/export")
def export_assessment(request: ISO27001AssessmentRequest):
    """
    Build an assessment and return a clean export-ready payload.

    This is a preparation hook — a future renderer (PDF/DOCX)
    would consume this payload to generate the final document.
    """
    try:
        evidence_rows = request.uploaded_rows
        if not evidence_rows and request.use_uploaded_evidence:
            evidence_rows = get_latest_assessment_evidence()

        result = build_assessment(
            framework="iso27001",
            uploaded_rows=evidence_rows,
            assessment_name=request.assessment_name,
            scope=request.scope,
            priority=request.priority,
            notes=request.notes,
        )
        return {"success": True, "export_payload": prepare_export_payload(result)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
