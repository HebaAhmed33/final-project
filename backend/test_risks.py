from services.contextual_risk_generator import generate_risks_from_data
import json

routing = {
    'routing_results': [
        {'source_type': 'employees', 'total_records': 100, 'no_security_training': 20, 'privileged_access_count': 5}
    ]
}
controls = [
    {'name': 'Access Control', 'domain': 'A.8', 'status': 'missing', 'severity': 'critical'},
    {'name': 'Asset Management', 'domain': 'A.5', 'status': 'missing', 'severity': 'high'}
]
present_types = {'employees', 'controls'}
all_sheets = [
    {'type': 'assets', 'rows': [
        {'asset_name': 'Unknown Server 1', 'asset_type': 'Server', 'criticality': 'high'},
        {'asset_name': 'Rogue Device 1', 'asset_type': 'IT Asset', 'criticality': 'medium'}
    ]},
    {'type': 'vendors', 'rows': [
        {'vendor_name': 'Bad Vendor LLC', 'service_type': 'Cloud Hosting', 'compliance': 'no', 'risk_level': 'high'}
    ]}
]

risks_iso = generate_risks_from_data(routing, controls, present_types, all_sheets, 'iso27001')
risks_hipaa = generate_risks_from_data(routing, controls, present_types, all_sheets, 'hipaa')

print('--- ISO 27001 ---')
for r in risks_iso:
    print(f"{r['threat']}: {r['risk_statement']}")

print('\n--- HIPAA ---')
for r in risks_hipaa:
    print(f"{r['threat']}: {r['risk_statement']}")
