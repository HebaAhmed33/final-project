import urllib.request
import json

url = "http://localhost:8000/upload/assessments"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    uploads = data.get("uploads", [])
    for latest in uploads[-5:]:
        print(f"---")
        print(f"Assessment Name: {latest.get('assessment_name')}")
        fw_assessment = latest.get('framework_assessment', {})
        print(f"Compliance Score (framework): {fw_assessment.get('compliance_score')}")
        print(f"Total Controls: {fw_assessment.get('total_controls')}")
        print(f"Compliant: {fw_assessment.get('compliant_controls')}")
        print(f"Partial: {fw_assessment.get('partial_controls')}")
        print(f"Missing: {fw_assessment.get('missing_controls')}")
