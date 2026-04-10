from app.extensions import db

class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(20), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey("cafe_tables.table_id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=False)
    order_time = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(20), default="pending")
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    payment_method = db.Column(db.String(30))
    note = db.Column(db.String(255))

    order_items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order {self.order_code}>"