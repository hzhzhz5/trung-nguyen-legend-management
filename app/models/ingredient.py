from app.extensions import db

class Ingredient(db.Model):
    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, primary_key=True)
    ingredient_code = db.Column(db.String(20), unique=True, nullable=False)
    ingredient_name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    min_stock_level = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default="active")

    inventory_records = db.relationship("StoreInventory", backref="ingredient", lazy=True)
    purchase_order_items = db.relationship("PurchaseOrderItem", backref="ingredient", lazy=True)
    inventory_transactions = db.relationship("InventoryTransaction", backref="ingredient", lazy=True)

    def __repr__(self):
        return f"<Ingredient {self.ingredient_name}>"