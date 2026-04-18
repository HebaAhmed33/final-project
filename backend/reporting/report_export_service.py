"""
Report Export Service.
Orchestrates loading a saved report, formatting it, and generating the PDF.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isms_core.report_history_manager import get_latest_report
from reporting.executive_report_formatter import format_executive_report
from reporting.pdf_report_generator import generate_executive_pdf


def export_company_latest_report_pdf(company_id: str, output_path: str):
    """
    Export the latest saved report for a company as a PDF.

    Parameters
    ----------
    company_id : str
        The company identifier used by the report history manager.
    output_path : str
        Destination file path for the generated PDF.

    Returns
    -------
    str or None
        *output_path* on success, ``None`` if no report exists for the company.
    """
    saved_report = get_latest_report(company_id)
    if saved_report is None:
        return None

    assessment_output = saved_report["assessment_output"]
    report_data = format_executive_report(assessment_output)
    generate_executive_pdf(report_data, output_path)
    return output_path


if __name__ == "__main__":
    company_id = "C001"
    pdf_path = f"{company_id}_executive_report.pdf"
    result = export_company_latest_report_pdf(company_id, pdf_path)
    if result:
        print(f"PDF exported -> {result}")
    else:
        print(f"No report found for company '{company_id}'.")
