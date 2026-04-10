from app.extensions import db

class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    purchase_order_item_id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.purchase_order_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    note = db.Column(db.String(255))

    def __repr__(self):
        return f"<PurchaseOrderItem {self.purchase_order_item_id}>"