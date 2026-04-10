from app.extensions import db

class OrderItem(db.Model):
    __tablename__ = "order_items"

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    note = db.Column(db.String(255))

    def __repr__(self):
        return f"<OrderItem {self.order_item_id}>"