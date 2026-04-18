import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _get_file_path(company_id):
    return os.path.join(DATA_DIR, f"{company_id}_reports.json")


def save_report(company_id, report):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _get_file_path(company_id)
    reports = get_reports(company_id)
    reports.append(report)
    with open(path, "w") as f:
        json.dump(reports, f, indent=2)


def get_reports(company_id):
    path = _get_file_path(company_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def get_latest_report(company_id):
    reports = get_reports(company_id)
    if not reports:
        return None
    return reports[-1]


if __name__ == "__main__":
    sample_report = {"title": "SmartISMS Assessment Report", "compliance_percentage": 60.0}
    save_report("C001", sample_report)
    print(get_reports("C001"))
    print(get_latest_report("C001"))
