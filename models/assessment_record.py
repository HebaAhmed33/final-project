class AssessmentRecord:
    def __init__(self, id: str, company_id: str, standard_ids: list, created_at: str, report_path: str, summary_snapshot: dict):
        self.id = id
        self.company_id = company_id
        self.standard_ids = standard_ids
        self.created_at = created_at
        self.report_path = report_path
        self.summary_snapshot = summary_snapshot
