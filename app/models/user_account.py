from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class UserAccount(UserMixin, db.Model):
    __tablename__ = "user_accounts"

    account_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), unique=True, nullable=True)
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.account_id)

    def __repr__(self):
        return f"<UserAccount {self.username}>"