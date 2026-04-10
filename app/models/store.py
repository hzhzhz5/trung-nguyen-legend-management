from app.extensions import db

class Store(db.Model):
    __tablename__ = "stores"

    store_id = db.Column(db.Integer, primary_key=True)
    store_code = db.Column(db.String(20), unique=True, nullable=False)
    store_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    open_time = db.Column(db.Time)
    close_time = db.Column(db.Time)
    status = db.Column(db.String(20), default="active")

    employees = db.relationship("Employee", backref="store", lazy=True)
    cafe_tables = db.relationship("CafeTable", backref="store", lazy=True)
    orders = db.relationship("Order", backref="store", lazy=True)

    def __repr__(self):
        return f"<Store {self.store_name}>"