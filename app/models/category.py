from app.extensions import db

class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(20), default="active")

    products = db.relationship("Product", backref="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.category_name}>"