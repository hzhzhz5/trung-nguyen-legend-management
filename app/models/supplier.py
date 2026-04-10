from app.extensions import db

class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(20), unique=True, nullable=False)
    supplier_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default="active")

    purchase_orders = db.relationship("PurchaseOrder", backref="supplier", lazy=True)

    def __repr__(self):
        return f"<Supplier {self.supplier_name}>"