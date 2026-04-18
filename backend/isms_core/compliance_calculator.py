def calculate_compliance(results):
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = total - passed
    percentage = (passed / total * 100) if total > 0 else 0.0
    return {
        "total_controls": total,
        "passed_controls": passed,
        "failed_controls": failed,
        "compliance_percentage": round(percentage, 2)
    }


if __name__ == "__main__":
    sample_results = [
        {"control_id": "ISO-0501", "control_name": "Information Security Policy", "status": "pass", "expected": True, "actual": True},
        {"control_id": "ISO-0601", "control_name": "Organization of Information Security", "status": "pass", "expected": True, "actual": True},
        {"control_id": "ISO-0801", "control_name": "Asset Management", "status": "fail", "expected": True, "actual": False},
        {"control_id": "ISO-0901", "control_name": "Access Control Policy", "status": "pass", "expected": True, "actual": True},
        {"control_id": "ISO-1201", "control_name": "Operational Security Procedures", "status": "fail", "expected": True, "actual": False}
    ]
    print(calculate_compliance(sample_results))
