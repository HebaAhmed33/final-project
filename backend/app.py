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
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from integration.full_combined_runner import run_full_combined_analysis
from isms_core.report_history_manager import get_reports, save_report
from isms_core.rule_engine import evaluate
from config_analysis.config_input_mapper import map_config_input
from config_analysis.technical_findings_formatter import format_technical_findings
from config_analysis.technical_risk_engine import create_technical_risks
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
from services.export_service import (
    get_latest_completed_assessment,
    build_excel_workbook,
    build_pdf_report,
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


class ConfigAnalysisRequest(BaseModel):
    raw_config_data: dict
    config_standard_file: str


class LoginRequest(BaseModel):
    email: str
    password: str





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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://62.171.128.179:3000", "http://62.171.128.179:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Audit Log — dedicated persistent activity log
# ---------------------------------------------------------------------------

_AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "audit_log.json")


def log_audit(action_type: str, detail: str, user: str = "", email: str = "", company: str = "", framework: str = "", score=None, metadata: dict = None):
    """Append an entry to the persistent audit log. Fire-and-forget."""
    try:
        os.makedirs(os.path.dirname(_AUDIT_LOG_PATH), exist_ok=True)
        entries = []
        if os.path.exists(_AUDIT_LOG_PATH):
            with open(_AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                entries = json.load(f)
        entries.append({
            "id": str(uuid.uuid4()),
            "type": action_type,
            "detail": detail,
            "user": user,
            "email": email,
            "company": company,
            "framework": framework,
            "score": score,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        with open(_AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Never break caller


@app.get("/")
def root():
    """Health check."""
    return {"message": "SmartISMS API running"}


@app.post("/login")
def login(request: LoginRequest):
    """Authenticate with hardcoded demo credentials."""
    if request.email == DEMO_USER["email"] and request.password == DEMO_USER["password"]:
        # Only log non-admin company user logins as business events
        if DEMO_USER["role"] != "admin":
            log_audit("login", "User logged in", email=request.email)
        return {
            "success": True,
            "user": {
                "id": DEMO_USER["id"],
                "company_id": DEMO_USER["company_id"],
                "email": DEMO_USER["email"],
                "role": DEMO_USER["role"],
            },
        }
    log_audit("login_failed", "Failed login attempt", email=request.email)
    return {"success": False, "message": "Invalid credentials"}





@app.post("/run-full-analysis")
def run_full_analysis(request: FullAnalysisRequest):
    """Run the full combined analysis pipeline."""
    result = run_full_combined_analysis(
        raw_data=request.raw_data,
        raw_config_data=request.raw_config_data,
        standard_file=request.standard_file,
        config_standard_file=request.config_standard_file,
    )
    # Not persisted to data files — audit log is the sole record
    log_audit("assessment", "Full combined analysis completed", framework="multiple", score=result.get("assessment", {}).get("assessment_summary", {}).get("compliance_score"))
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
    # Report is persisted to *_reports.json — dashboard reads that file directly
    return stored_report



# Run: uvicorn backend.app:app --reload
# ---------------------------------------------------------------------------


@app.post("/run-config-analysis")
def run_config_analysis(request: ConfigAnalysisRequest):
    """Run config-only technical analysis."""
    normalized = map_config_input(request.raw_config_data)
    results = evaluate(normalized, request.config_standard_file)
    findings = format_technical_findings(results)
    risks = create_technical_risks(results)
    # This endpoint returns results in-memory only (no persistence) — no audit needed
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
        # process_assessment_upload persists to assessment uploads data file
        # Dashboard reads that file directly — no audit duplication needed
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
    framework: str = Form("cis"),
):
    """Upload a configuration file (JSON / YAML / ENV) for processing.

    The ``framework`` parameter selects which compliance framework to map
    findings against (cis, nist, iso27001).  This uses the Configuration
    Compliance Engine which is fully isolated from the Assessment Engine.
    """
    # process_config_upload persists to config_uploads.json
    # Dashboard reads that file directly — no audit duplication needed
    result = await process_config_upload(file=file, framework=framework)
    return result


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

        # Save to history — dashboard reads assessment_history.json directly
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
        log_audit("report", f"Export assessment payload generated", framework="ISO27001", metadata={"assessment_name": request.assessment_name})
        return {"success": True, "export_payload": prepare_export_payload(result)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Export download endpoints
# ---------------------------------------------------------------------------

@app.get("/export/latest/excel")
def export_latest_excel():
    """Download an Excel workbook of the latest completed assessment."""
    fa = get_latest_completed_assessment()
    if not fa:
        raise HTTPException(
            status_code=404,
            detail="No completed assessment results found. Run an assessment first.",
        )
    buf, filename = build_excel_workbook(fa)
    log_audit("report", "Exported latest assessment to Excel")
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/export/latest/pdf")
def export_latest_pdf():
    """Download a PDF report of the latest completed assessment."""
    fa = get_latest_completed_assessment()
    if not fa:
        raise HTTPException(
            status_code=404,
            detail="No completed assessment results found. Run an assessment first.",
        )
    buf, filename = build_pdf_report(fa)
    log_audit("report", "Exported latest assessment to PDF")
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Live Configuration Scan endpoints (isolated — does NOT modify existing logic)
# ---------------------------------------------------------------------------

from live_scan.live_scanner import run_live_scan, get_scan_history


class LiveScanRequest(BaseModel):
    host: str
    port: int = 22
    username: str
    private_key: str
    framework: str = "iso27001"


@app.post("/live-scan/start")
async def start_live_scan(request: LiveScanRequest):
    """
    Execute a live SSH-based configuration scan on a remote host.

    Security: Uses read-only commands from a strict whitelist.
    Credentials are used in-memory only and never stored or logged.
    """
    # Validate framework
    allowed_frameworks = ["iso27001", "nist", "cis"]
    fw = request.framework.lower()
    if fw not in allowed_frameworks:
        raise HTTPException(status_code=400, detail=f"Unsupported framework: {request.framework}. Allowed: {allowed_frameworks}")

    # Validate host
    if not request.host or not request.host.strip():
        raise HTTPException(status_code=400, detail="Target host is required.")

    # Validate port
    if request.port < 1 or request.port > 65535:
        raise HTTPException(status_code=400, detail="Port must be between 1 and 65535.")

    # Validate private key content (by headers, not filename)
    valid_headers = ["BEGIN OPENSSH PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY", "BEGIN DSA PRIVATE KEY", "BEGIN PRIVATE KEY"]
    if not request.private_key or not any(h in request.private_key for h in valid_headers):
        raise HTTPException(status_code=400, detail="Invalid SSH private key format. The file must contain a valid private key (OpenSSH, RSA, EC, or PEM format).")

    try:
        # run_live_scan persists to live_scan_history.json
        # Dashboard reads that file directly — no audit duplication needed
        result = run_live_scan(
            host=request.host.strip(),
            port=request.port,
            username=request.username.strip(),
            private_key_content=request.private_key,
            framework=fw,
        )
        return result
    except Exception as exc:
        log_audit("live_scan_failed", f"Live scan failed: {request.host.strip()} — {str(exc)}", framework=fw)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(exc)}")


@app.get("/live-scan/history")
def live_scan_history():
    """Return all past live scan summaries (no credentials stored)."""
    return {"history": get_scan_history()}


# ---------------------------------------------------------------------------
# Admin Dashboard endpoints (read-only aggregation — isolated)
# ---------------------------------------------------------------------------

@app.get("/admin/dashboard")
def admin_dashboard():
    """Aggregate all system data for admin monitoring. Read-only."""
    import glob

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    def _read_json(path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    # Onboarding clients (from frontend data dir)
    clients_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "data", "clients.json")
    clients = _read_json(clients_path)

    # Assessment history (scored runs from /assess/iso27001)
    assessment_runs = _read_json(os.path.join(data_dir, "assessment_history.json"))

    # Assessment uploads (raw evidence uploads from /upload/assessment)
    assessment_uploads = _read_json(os.path.join(data_dir, "assessments.json"))

    # Merge both sources — scored runs take priority, uploads fill in the rest
    _seen_ids = {a.get("id") for a in assessment_runs}
    assessments = list(assessment_runs)  # start with scored runs
    for au in assessment_uploads:
        if au.get("id") not in _seen_ids:
            # Score & controls live inside framework_assessment for uploads
            fa = au.get("framework_assessment") or {}
            assessments.append({
                "id": au.get("id"),
                "assessment_name": au.get("assessment_name", ""),
                "framework": au.get("framework", ""),
                "compliance_score": fa.get("compliance_score"),
                "priority": au.get("priority") or fa.get("priority", ""),
                "evidence_used": bool(au.get("rows")),
                "total_controls": fa.get("total_controls") or au.get("total_rows", 0),
                "compliant_controls": fa.get("compliant_controls", 0),
                "missing_controls": fa.get("missing_controls", 0),
                "created_at": au.get("created_at", ""),
            })
            _seen_ids.add(au.get("id"))

    # Config uploads
    config_uploads = _read_json(os.path.join(data_dir, "config_uploads.json"))

    # Live scan history
    live_scans = _read_json(os.path.join(data_dir, "live_scan_history.json"))

    # Reports
    reports = []
    for rpt_file in glob.glob(os.path.join(data_dir, "*_reports.json")):
        rpt_data = _read_json(rpt_file)
        if isinstance(rpt_data, list):
            reports.extend(rpt_data)

    # Dedicated audit log (captures login, exports, admin actions, etc.)
    audit_entries = _read_json(os.path.join(data_dir, "audit_log.json"))

    # Build activity timeline — merge data-file entries + audit log
    activity = []
    for c in clients:
        activity.append({
            "type": "onboarding",
            "timestamp": c.get("createdAt", ""),
            "user": c.get("employeeName", "Unknown"),
            "email": c.get("workEmail", ""),
            "company": c.get("companyName", ""),
            "detail": f"Onboarding submitted — {c.get('companyType', '')}",
            "framework": "",
            "score": None,
        })
    for a in assessments:
        activity.append({
            "type": "assessment",
            "timestamp": a.get("created_at", ""),
            "user": "",
            "email": "",
            "company": "",
            "detail": f"Assessment: {a.get('assessment_name', 'Unnamed')}",
            "framework": a.get("framework", ""),
            "score": a.get("compliance_score"),
        })
    for cu in config_uploads:
        activity.append({
            "type": "config_upload",
            "timestamp": cu.get("created_at", ""),
            "user": "",
            "email": "",
            "company": "",
            "detail": f"Config uploaded: {cu.get('file_name', 'unknown')}",
            "framework": cu.get("framework", ""),
            "score": None,
        })
    for ls in live_scans:
        activity.append({
            "type": "live_scan",
            "timestamp": ls.get("timestamp", ""),
            "user": "",
            "email": "",
            "company": "",
            "detail": f"Live scan: {ls.get('target_host', 'unknown')}",
            "framework": ls.get("framework", ""),
            "score": ls.get("compliance_score"),
        })
    for r in reports:
        activity.append({
            "type": "report",
            "timestamp": r.get("created_at", ""),
            "user": "",
            "email": "",
            "company": r.get("company_name", ""),
            "detail": f"Report generated — {r.get('company_name', '')}",
            "framework": "",
            "score": None,
        })
    # Merge audit log entries that are NOT already covered by data files.
    # Data files already provide: onboarding, assessment, config_upload,
    # live_scan, report.  Audit log adds: login, login_failed,
    # admin_action, live_scan_failed, and report exports.
    _DATA_FILE_TYPES = {"onboarding", "assessment", "config_upload", "live_scan"}
    for ae in audit_entries:
        ae_type = ae.get("type", "system")
        if ae_type in _DATA_FILE_TYPES:
            continue  # already represented from data file above
        activity.append({
            "type": ae_type,
            "timestamp": ae.get("timestamp", ""),
            "user": ae.get("user", ""),
            "email": ae.get("email", ""),
            "company": ae.get("company", ""),
            "detail": ae.get("detail", ""),
            "framework": ae.get("framework", ""),
            "score": ae.get("score"),
        })

    # Sort by timestamp descending
    activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Compute avg compliance score
    scored = [a.get("compliance_score", 0) for a in assessments if a.get("compliance_score") is not None]
    avg_score = round(sum(scored) / len(scored), 1) if scored else 0

    # Unique companies from onboarding
    unique_companies = list({c.get("companyName", "").strip() for c in clients if c.get("companyName", "").strip()})

    return {
        "stats": {
            "total_companies": len(unique_companies),
            "total_assessments": len(assessments),
            "total_config_reviews": len(config_uploads),
            "total_live_scans": len(live_scans),
            "total_reports": len(reports),
            "avg_compliance_score": avg_score,
        },
        "companies": unique_companies,
        "clients": clients,
        "assessments": [
            {
                "id": a.get("id"),
                "name": a.get("assessment_name", ""),
                "framework": a.get("framework", ""),
                "score": a.get("compliance_score"),
                "priority": a.get("priority", ""),
                "evidence_used": a.get("evidence_used", False),
                "total_controls": a.get("total_controls", 0),
                "compliant": a.get("compliant_controls", 0),
                "missing": a.get("missing_controls", 0),
                "created_at": a.get("created_at", ""),
            }
            for a in assessments
        ],
        "config_uploads": [
            {
                "id": cu.get("id"),
                "file_name": cu.get("file_name", ""),
                "file_type": cu.get("file_type", ""),
                "framework": cu.get("framework", ""),
                "risk": cu.get("config_analysis", {}).get("summary", {}).get("overall_risk", "N/A") if cu.get("config_analysis") else (cu.get("config_compliance", {}).get("summary", {}).get("overall_risk", "N/A") if cu.get("config_compliance") else "N/A"),
                "findings": cu.get("config_analysis", {}).get("summary", {}).get("total_findings", 0) if cu.get("config_analysis") else 0,
                "score": cu.get("config_compliance", {}).get("compliance", {}).get("compliance_score") if cu.get("config_compliance") else None,
                "created_at": cu.get("created_at", ""),
            }
            for cu in config_uploads
        ],
        "live_scans": live_scans,
        "reports": [
            {
                "company_id": r.get("company_id", ""),
                "company_name": r.get("company_name", ""),
                "created_at": r.get("created_at", ""),
                "compliance": r.get("assessment_output", {}).get("assessment_summary", {}).get("compliance_percentage"),
            }
            for r in reports
        ],
        "activity": activity[:500],
    }


# --- Admin helper: read/write JSON safely ---
def _admin_read_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def _admin_write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Admin: Client/User actions ---

_CLIENTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "data", "clients.json")

@app.delete("/admin/clients/{client_id}")
def admin_delete_client(client_id: str):
    """Delete a client by ID."""
    clients = _admin_read_json(_CLIENTS_PATH)
    before = len(clients)
    clients = [c for c in clients if str(c.get("id", "")) != client_id]
    if len(clients) == before:
        raise HTTPException(status_code=404, detail="Client not found")
    _admin_write_json(_CLIENTS_PATH, clients)
    log_audit("admin_action", f"Client deleted: {client_id}", metadata={"client_id": client_id})
    return {"success": True, "message": "Client deleted"}

@app.post("/admin/clients/{client_id}/ban")
def admin_ban_client(client_id: str):
    """Ban a client — sets status to 'banned'."""
    clients = _admin_read_json(_CLIENTS_PATH)
    found = False
    for c in clients:
        if str(c.get("id", "")) == client_id:
            c["status"] = "banned"
            c["banned_at"] = datetime.now(timezone.utc).isoformat()
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Client not found")
    _admin_write_json(_CLIENTS_PATH, clients)
    log_audit("admin_action", f"Client banned: {client_id}", metadata={"client_id": client_id})
    return {"success": True, "message": "Client banned"}

@app.post("/admin/clients/{client_id}/unban")
def admin_unban_client(client_id: str):
    """Unban a client — sets status to 'active'."""
    clients = _admin_read_json(_CLIENTS_PATH)
    found = False
    for c in clients:
        if str(c.get("id", "")) == client_id:
            c["status"] = "active"
            c.pop("banned_at", None)
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Client not found")
    _admin_write_json(_CLIENTS_PATH, clients)
    log_audit("admin_action", f"Client unbanned: {client_id}", metadata={"client_id": client_id})
    return {"success": True, "message": "Client unbanned"}


# --- Admin: Assessment actions ---

_ASSESS_HIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "assessment_history.json")

@app.delete("/admin/assessments/{assessment_id}")
def admin_delete_assessment(assessment_id: str):
    """Delete an assessment from history by ID."""
    items = _admin_read_json(_ASSESS_HIST_PATH)
    before = len(items)
    items = [a for a in items if str(a.get("id", "")) != assessment_id]
    if len(items) == before:
        raise HTTPException(status_code=404, detail="Assessment not found")
    _admin_write_json(_ASSESS_HIST_PATH, items)
    log_audit("admin_action", f"Assessment deleted: {assessment_id}", metadata={"assessment_id": assessment_id})
    return {"success": True, "message": "Assessment deleted"}


# --- Admin: Config upload actions ---

_CONFIG_UPL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "config_uploads.json")

@app.delete("/admin/configs/{config_id}")
def admin_delete_config(config_id: str):
    """Delete a config upload entry by ID."""
    items = _admin_read_json(_CONFIG_UPL_PATH)
    before = len(items)
    items = [c for c in items if str(c.get("id", "")) != config_id]
    if len(items) == before:
        raise HTTPException(status_code=404, detail="Config upload not found")
    _admin_write_json(_CONFIG_UPL_PATH, items)
    log_audit("admin_action", f"Config upload deleted: {config_id}", metadata={"config_id": config_id})
    return {"success": True, "message": "Config upload deleted"}
