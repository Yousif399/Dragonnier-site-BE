from config import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(60), unique=True, nullable=False)
    product_price = db.Column(db.Numeric(7, 2))
    product_img = db.Column(db.String)
    product_quantity = db.Column(db.Integer)

    def to_json(self):
        return {
            "id": self.id,
            "productName": self.product_name,
            "productPrice": self.product_price,
            "productImg": self.product_img,
            "productQuantity": self.product_quantity
        }