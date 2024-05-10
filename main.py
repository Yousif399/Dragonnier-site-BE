from flask import request, json, jsonify
from config import app, db
from models import Product


# CRUD

# Get Products
@app.route('/product', methods=['GET'])
def get_product():
    products = Product.query.all()
    product_list = [p.to_json() for p in products]
    return jsonify({
        "status": "Ok",
        "products": product_list
    })

# Create product
@app.route('/create-product', methods=['POST'])
def create_products():
    product_name = request.json.get("productName")
    product_price = request.json.get("productPrice")
    product_img = request.json.get("productImg")
    product_quantity = request.json.get("productQuantity")

    if not product_name or not product_price or not product_img or not product_quantity:
        return (jsonify({"Message": "Make sure you entered your correct info"}), 400)

    new_product = Product(product_name=product_name,
                          product_price=product_price,
                          product_img=product_img,
                          product_quantity=product_quantity) 
    try:
        db.session.add(new_product)
        db.session.commit()
    except Exception as ex:
        return jsonify({"Message": str(ex)}), 400
    
    return jsonify({"Message": "User created"}), 201


# Update product
@app.route("/update-product/<int:id>", methods = ["PATCH"])
def update_product(id):
    product = Product.query.get(id)

    if not product:
        print('no product found')
        return jsonify({"Message":"Product was not founded"}), 404
    
    data = request.json
    product.product_name = data.get("productName", product.product_name)
    product.product_price = data.get("productPrice", product.product_price)
    product.product_img = data.get("productImg", product.product_img)
    product.product_quantity = data.get("productQuantity", product.product_quantity)

    db.session.commit()

    return jsonify({"Message": "Product updated"}), 200

# Delete product
@app.route("/delete-product/<int:id>", methods = ["DELETE"])
def delete_product(id):
    product = Product.query.get(id)

    if not product:
        print('No product found')
        return jsonify({"Message": "Product was not founded to delete"}), 404
    
    db.session.delete(product)
    db.session.commit()

    return jsonify({"Message": "Product was deleted successfully"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
