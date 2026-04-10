from app.extensions import db

class Employee(db.Model):
    __tablename__ = "employees"

    employee_id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    hire_date = db.Column(db.Date)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    status = db.Column(db.String(20), default="active")

    user_account = db.relationship("UserAccount", backref="employee", uselist=False)
    orders = db.relationship("Order", backref="employee", lazy=True)
    
    def __repr__(self):
        return f"<Employee {self.full_name}>"