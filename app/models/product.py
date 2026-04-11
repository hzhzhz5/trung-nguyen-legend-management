from app.extensions import db

class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(20), unique=True, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.category_id"), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # thêm mới
    quantity_in_stock = db.Column(db.Integer, nullable=False, default=0)

    description = db.Column(db.String(255))
    image_url = db.Column(db.Text)
    status = db.Column(db.String(20), default="available")
    order_items = db.relationship("OrderItem", backref="product", lazy=True)

    def __repr__(self):
        return f"<Product {self.product_name}>"