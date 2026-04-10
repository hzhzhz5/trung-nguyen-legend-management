from app.extensions import db

class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    purchase_order_id = db.Column(db.Integer, primary_key=True)
    purchase_order_code = db.Column(db.String(20), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.supplier_id"), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=True)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(20), default="draft")
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    note = db.Column(db.String(255))

    store = db.relationship("Store", backref="purchase_orders", lazy=True)
    creator = db.relationship("Employee", backref="purchase_orders", lazy=True, foreign_keys=[created_by])

    items = db.relationship(
        "PurchaseOrderItem",
        backref="purchase_order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PurchaseOrder {self.purchase_order_code}>"