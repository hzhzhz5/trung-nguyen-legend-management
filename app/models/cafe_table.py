from app.extensions import db

class CafeTable(db.Model):
    __tablename__ = "cafe_tables"

    table_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.store_id"), nullable=False)
    table_code = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    status = db.Column(db.String(20), default="empty")
    orders = db.relationship("Order", backref="table", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("store_id", "table_code", name="uq_store_table_code"),
    )

    def __repr__(self):
        return f"<CafeTable {self.table_code}>"