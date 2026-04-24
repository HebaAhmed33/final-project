import requests
import io
import openpyxl

wb = openpyxl.Workbook()

# First sheet: Title-style
ws1 = wb.active
ws1.title = "Aegis.One_Multi_Sheet_Upload_Template"
ws1.append(["Organization Profile"])
ws1.append(["Field", "Value"])
ws1.append(["Company Name", "Test Corp"])

# Second sheet: Controls
ws2 = wb.create_sheet("Controls")
ws2.append(["Control ID", "Control Name", "Status", "Owner"])
ws2.append(["A.5.1", "Information Security Policy", "Implemented", "CISO"])

buf = io.BytesIO()
wb.save(buf)
contents = buf.getvalue()

files = {'file': ('test.xlsx', contents, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
data = {
    'assessment_name': 'Test Upload',
    'framework': 'iso27001',
    'priority': 'Medium',
    'notes': 'Test notes'
}

response = requests.post('http://127.0.0.1:8001/upload/assessment', files=files, data=data)

print(response.status_code)
import json
print(json.dumps(response.json(), indent=2))
