from app.extensions import db

class InventoryTransaction(db.Model):
    __tablename__ = "inventory_transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    reference_type = db.Column(db.String(30))
    reference_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    note = db.Column(db.String(255))

    store = db.relationship("Store", backref="inventory_transactions", lazy=True)
    creator = db.relationship("Employee", backref="inventory_transactions", lazy=True, foreign_keys=[created_by])

    def __repr__(self):
        return f"<InventoryTransaction {self.transaction_id}>"