class User:
    def __init__(self, id: str, company_id: str, email: str, password_hash: str, role: str):
        self.id = id
        self.company_id = company_id
        self.email = email
        self.password_hash = password_hash
        self.role = role
