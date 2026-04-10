from app.extensions import db

class StoreInventory(db.Model):
    __tablename__ = "store_inventory"

    inventory_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.ingredient_id"), nullable=False)
    quantity_on_hand = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    last_updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    store = db.relationship("Store", backref="inventory_records", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("store_id", "ingredient_id", name="uq_store_ingredient_inventory"),
    )

    def __repr__(self):
        return f"<StoreInventory store={self.store_id} ingredient={self.ingredient_id}>"