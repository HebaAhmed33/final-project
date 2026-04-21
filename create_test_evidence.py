import pandas as pd

data = [
    {
        "control_id": "ISO-A6.1-01",
        "status": "compliant",
        "reference": "HR Background Check Policy v1.2",
    },
    {
        "control_id": "ISO-A6.2-01",
        "status": "compliant",
        "reference": "Employee Handbook - Security Addendum",
    },
    {
        "control_id": "ISO-A6.3-01",
        "status": "partial",
        "reference": "Annual Security Training Log 2024 (Missing 5%)",
    },
    {
        "control_id": "ISO-A6.4-01",
        "status": "compliant",
        "reference": "Disciplinary Process Guideline.pdf",
    },
    {
        "rule_id": "ISO-A6.7-01",  # Test using rule_id instead of control_id
        "status": "missing",
        "reference": "", # Missing evidence
    }
]

df = pd.DataFrame(data)
df.to_excel("test_iso_evidence.xlsx", index=False)
print("Created test_iso_evidence.xlsx")
