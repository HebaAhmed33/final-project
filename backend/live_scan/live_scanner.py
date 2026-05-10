"""
Live Configuration Scanner.

Connects to a remote host via SSH (read-only), fetches configuration
files/outputs using a strict command whitelist, then analyses the
collected data and maps findings to a compliance framework.

Security constraints:
  - Read-only operations only
  - No remote writes or modifications
  - Strict command whitelist — no arbitrary execution
  - Private keys used in-memory only, never stored
  - No credential persistence
"""

import io
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from typing import Any

import paramiko

from config_analysis.raw_config_analyzer import (
    analyze_raw_config,
    _FRAMEWORK_CONTROL_MAP,
)


# ---------------------------------------------------------------------------
# Command whitelist — ONLY these commands may be executed on remote hosts
# ---------------------------------------------------------------------------

COMMAND_WHITELIST: list[dict[str, str]] = [
    {"id": "sshd_config", "cmd": "cat /etc/ssh/sshd_config", "label": "SSH Configuration"},
    {"id": "ufw_status", "cmd": "ufw status verbose", "label": "UFW Firewall Status"},
    {"id": "iptables", "cmd": "iptables -L -n -v 2>/dev/null || echo 'iptables not available'", "label": "IPTables Rules"},
    {"id": "nginx_conf", "cmd": "cat /etc/nginx/nginx.conf 2>/dev/null || echo 'nginx not installed'", "label": "Nginx Configuration"},
    {"id": "services", "cmd": "systemctl list-units --type=service --state=running --no-pager 2>/dev/null || service --status-all 2>/dev/null || echo 'service listing not available'", "label": "Running Services"},
    {"id": "open_ports", "cmd": "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo 'port listing not available'", "label": "Open Ports"},
    {"id": "os_info", "cmd": "cat /etc/os-release 2>/dev/null || uname -a", "label": "OS Information"},
    {"id": "passwd_policy", "cmd": "cat /etc/login.defs 2>/dev/null | grep -E 'PASS_MAX_DAYS|PASS_MIN_DAYS|PASS_MIN_LEN|PASS_WARN_AGE' || echo 'password policy not available'", "label": "Password Policy"},
    {"id": "sudoers", "cmd": "cat /etc/sudoers 2>/dev/null | grep -v '^#' | grep -v '^$' || echo 'sudoers not readable'", "label": "Sudoers Configuration"},
    {"id": "fail2ban", "cmd": "fail2ban-client status 2>/dev/null || echo 'fail2ban not installed'", "label": "Fail2Ban Status"},
]


# ---------------------------------------------------------------------------
# SSH connection + command execution
# ---------------------------------------------------------------------------

def _connect_ssh(host: str, port: int, username: str, private_key_content: str) -> paramiko.SSHClient:
    """Establish an SSH connection using an in-memory private key."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Parse the private key from content string
    key_file = io.StringIO(private_key_content)
    try:
        pkey = paramiko.RSAKey.from_private_key(key_file)
    except paramiko.SSHException:
        key_file.seek(0)
        try:
            pkey = paramiko.Ed25519Key.from_private_key(key_file)
        except paramiko.SSHException:
            key_file.seek(0)
            try:
                pkey = paramiko.ECDSAKey.from_private_key(key_file)
            except paramiko.SSHException:
                raise ValueError("Unsupported SSH key format. Please use RSA, Ed25519, or ECDSA keys.")

    client.connect(
        hostname=host,
        port=port,
        username=username,
        pkey=pkey,
        timeout=15,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def _execute_whitelisted_command(client: paramiko.SSHClient, cmd: str, timeout: int = 30) -> str:
    """Execute a single whitelisted command and return stdout."""
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode("utf-8", errors="replace")
    return output.strip()


# ---------------------------------------------------------------------------
# Scan orchestrator
# ---------------------------------------------------------------------------

def run_live_scan(
    host: str,
    port: int,
    username: str,
    private_key_content: str,
    framework: str = "iso27001",
) -> dict[str, Any]:
    """
    Execute a full live configuration scan.

    Returns a structured result dict compatible with the configuration
    results page format.
    """
    progress: list[dict] = []
    collected_configs: dict[str, str] = {}
    scan_start = datetime.now(timezone.utc)

    def _log(msg: str, status: str = "running"):
        progress.append({
            "message": msg,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # Step 1: Connect
    _log("Connecting to target...")
    try:
        client = _connect_ssh(host, port, username, private_key_content)
    except ValueError as e:
        _log(str(e), "error")
        return {"success": False, "error": str(e), "progress": progress}
    except Exception as e:
        msg = f"SSH connection failed: {str(e)}"
        _log(msg, "error")
        return {"success": False, "error": msg, "progress": progress}

    _log("Authenticating...", "success")
    _log("Connected successfully.", "success")

    # Step 2: Execute whitelisted commands
    for cmd_entry in COMMAND_WHITELIST:
        _log(f"Fetching {cmd_entry['label']}...")
        try:
            output = _execute_whitelisted_command(client, cmd_entry["cmd"])
            collected_configs[cmd_entry["id"]] = output
            _log(f"Collected {cmd_entry['label']}.", "success")
        except Exception as e:
            collected_configs[cmd_entry["id"]] = f"Error: {str(e)}"
            _log(f"Could not fetch {cmd_entry['label']}: {str(e)}", "warning")

    # Step 3: Close connection
    client.close()
    _log("SSH session closed.")

    # Step 4: Analyse collected configurations
    _log("Parsing configurations...")
    all_findings = []
    all_components = []
    config_types_found = []

    # Combine all collected output into one large text for the analyzer
    combined_text = ""
    for config_id, output in collected_configs.items():
        if output and "not available" not in output.lower() and "not installed" not in output.lower() and "not readable" not in output.lower() and not output.startswith("Error:"):
            combined_text += f"\n# === {config_id} ===\n{output}\n"

    if combined_text.strip():
        _log("Evaluating controls...")
        analysis = analyze_raw_config(combined_text, "live_scan_output.conf", framework)
        all_findings = analysis.get("findings", [])
        all_components = analysis.get("components", [])
        config_types_found.append(analysis.get("config_type", "system"))

    # Step 5: Build per-config analysis for detail
    per_config_analysis = {}
    for config_id, output in collected_configs.items():
        if output and not output.startswith("Error:") and "not available" not in output.lower() and "not installed" not in output.lower():
            label = next((c["label"] for c in COMMAND_WHITELIST if c["id"] == config_id), config_id)
            per_config_analysis[config_id] = {
                "label": label,
                "output_length": len(output),
                "has_content": True,
            }
        else:
            label = next((c["label"] for c in COMMAND_WHITELIST if c["id"] == config_id), config_id)
            per_config_analysis[config_id] = {
                "label": label,
                "output_length": 0,
                "has_content": False,
            }

    # Step 6: Calculate compliance score
    _log("Calculating compliance score...")
    total_checks = len(COMMAND_WHITELIST)
    total_findings = len(all_findings)
    high_count = sum(1 for f in all_findings if f.get("severity") == "High")
    medium_count = sum(1 for f in all_findings if f.get("severity") == "Medium")
    low_count = sum(1 for f in all_findings if f.get("severity") == "Low")

    # Score: start at 100, deduct for findings
    score = max(0, 100 - (high_count * 15) - (medium_count * 8) - (low_count * 3))

    if score >= 80:
        overall_risk = "Low"
    elif score >= 60:
        overall_risk = "Medium"
    else:
        overall_risk = "High"

    # Framework label mapping
    fw_labels = {
        "iso27001": "ISO 27001",
        "nist": "NIST 800-53",
        "cis": "CIS Controls",
    }

    _log("Generating report...", "success")

    scan_end = datetime.now(timezone.utc)
    _log("Scan completed.", "success")

    # Step 7: Build result
    result = {
        "success": True,
        "scan_type": "live_scan",
        "target_host": host,
        "framework": framework,
        "framework_label": fw_labels.get(framework, framework.upper()),
        "scan_timestamp": scan_start.isoformat(),
        "scan_duration_seconds": (scan_end - scan_start).total_seconds(),
        "config_analysis": {
            "summary": {
                "config_type": "live_system_scan",
                "total_findings": total_findings,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
                "overall_risk": overall_risk,
            },
            "components": all_components,
        },
        "config_compliance": {
            "compliance": {
                "compliance_score": score,
            },
            "framework_label": fw_labels.get(framework, framework.upper()),
            "findings": all_findings,
            "risk_register": [],
            "best_practices": _generate_best_practices(all_findings, framework),
        },
        "collected_configs": per_config_analysis,
        "progress": progress,
    }

    # Save to history
    _save_scan_history(result)

    return result


# ---------------------------------------------------------------------------
# Best practices generator
# ---------------------------------------------------------------------------

def _generate_best_practices(findings: list[dict], framework: str) -> list[dict]:
    """Generate best practice recommendations based on findings."""
    practices = []
    seen_categories = set()

    for f in findings:
        cat = f.get("category", "General")
        if cat not in seen_categories:
            seen_categories.add(cat)
            practices.append({
                "title": f"Strengthen {cat}",
                "category": cat,
                "description": f.get("recommendation", f"Review and improve {cat} controls."),
            })

    # Add general practices if few findings
    if len(practices) < 3:
        defaults = [
            {"title": "Enable System Auditing", "category": "Monitoring", "description": "Configure auditd or equivalent to track security-relevant events."},
            {"title": "Implement Regular Patching", "category": "Maintenance", "description": "Establish automated patching for OS and applications."},
            {"title": "Review Access Controls", "category": "Access Control", "description": "Regularly audit user accounts, sudo permissions, and SSH access."},
        ]
        for d in defaults:
            if d["category"] not in seen_categories:
                practices.append(d)

    return practices[:6]


# ---------------------------------------------------------------------------
# Scan history persistence (isolated)
# ---------------------------------------------------------------------------

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "live_scan_history.json")


def _save_scan_history(result: dict) -> None:
    """Append a scan summary to the history file. Never stores credentials."""
    summary = {
        "timestamp": result.get("scan_timestamp"),
        "target_host": result.get("target_host"),
        "framework": result.get("framework"),
        "framework_label": result.get("framework_label"),
        "compliance_score": result.get("config_compliance", {}).get("compliance", {}).get("compliance_score"),
        "total_findings": result.get("config_analysis", {}).get("summary", {}).get("total_findings", 0),
        "high": result.get("config_analysis", {}).get("summary", {}).get("high", 0),
        "medium": result.get("config_analysis", {}).get("summary", {}).get("medium", 0),
        "low": result.get("config_analysis", {}).get("summary", {}).get("low", 0),
        "overall_risk": result.get("config_analysis", {}).get("summary", {}).get("overall_risk"),
        "scan_duration_seconds": result.get("scan_duration_seconds"),
        "success": result.get("success", False),
    }

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    history.append(summary)

    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_scan_history() -> list[dict]:
    """Return all scan history entries."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
