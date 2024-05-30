from flask import request, json, jsonify, render_template, send_file
from config import app, db, basedir
from models import Product
from flask_mail import Mail, Message
import os
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import ssl

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
@app.route("/update-product/<int:id>", methods=["PATCH"])
def update_product(id):
    product = Product.query.get(id)

    if not product:
        print('no product found')
        return jsonify({"Message": "Product was not founded"}), 404

    data = request.json
    product.product_name = data.get("productName", product.product_name)
    product.product_price = data.get("productPrice", product.product_price)
    product.product_img = data.get("productImg", product.product_img)
    product.product_quantity = data.get(
        "productQuantity", product.product_quantity)

    db.session.commit()

    return jsonify({"Message": "Product updated"}), 200

# Delete product


@app.route("/delete-product/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)

    if not product:
        print('No product found')
        return jsonify({"Message": "Product was not founded to delete"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"Message": "Product was deleted successfully"}), 200


mail = Mail(app)


def send_confirmation(recipient):
    msg = Message('Order Confirmation',
                  sender='joseph.ahmed65@yahoo.com', recipients=[recipient])
    # msg.html = render_template('index.html')
    msg.body = "HELLLLLOPOOOO"
    mail.send(msg)


def send_notification(order, recipient):
    msg = Message('Order Confirmation',
                  sender='joseph.ahmed65@yahoo.com', recipients=[recipient])
    # msg.html = render_template('index.html')
    msg.body = "HELLLLLOPOOOOooo"

    mail.send(msg)


ssl._create_default_https_context = ssl._create_unverified_context
@app.route('/image')
def serve_image():
    image_path = 'images/DragonnierLogo.png'
    return send_file(image_path, mimetype='image/jpeg')

@app.route('/place-order', methods=['POST'])
def place_order():
    # order = process_order(request.form)
    data = request.json
    image = serve_image()
    print(image)

    email_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                width: 100%;
                max-width: 600px;
                margin: auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: rgb(240, 248, 255);
            }}

            .input-wrapper {{
                display: flex;
                gap: 25px;
            }}
            h2 {{
                color: black;
                font-weight: bolder;
            }}
            .order-details, .shipping-info {{
                margin-bottom: 20px;
            }}
            .order-details h3, .shipping-info h3 {{
                margin-bottom: 5px;
                color: #555;
            }}
            .order-details div, .shipping-info div {{
                margin-bottom: 10px;
            }}
            .total {{
                font-weight: bold;
            }}
            .footer {{
                margin-top: 20px;
                text-align: center;
                font-size: 0.9em;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
        <div class="input-wrapper"> 
         <img src="http://127.0.0.1:5000/image" alt="Logo" width="60">
            <h2>Thank You for Your Order, {data['name']}!</h2>
        </div>
            <div class="order-details">
                <h3>Order Details:</h3>
                <div><strong>Product:</strong> {data['product']}</div>
                <div><strong>Quantity:</strong> {data['quantity']}</div>
                <div><strong>Subtotal:</strong> ${data['subtotal']}</div>
                <div><strong>Taxes:</strong> ${data['taxes']}</div>
                <div class="total"><strong>Total:</strong> ${data['total']}</div>
            </div>
            <div class="shipping-info">
                <h3>Shipping Information:</h3>
                <div><strong>Name:</strong> {data['name']}</div>
                <div><strong>Address:</strong> {data['address']}</div>
                <div><strong>City:</strong> {data['city']}</div>
                <div><strong>Postal Code:</strong> {data['postalCode']}</div>
                <div><strong>Phone Number:</strong> {data['phone']}</div>
                <div><strong>Company:</strong> {data['company']}</div>
            </div>
            <h3>Your order is now being processed and we will notify you once it has been shipped. If you have any questions or need to make changes to your order, please feel free to contact us at [Customer Support Email or Phone Number].</h3>
        </div>
    </body>
    </html>
    """
    msg = Message(subject='Order Confirmation', sender='help@dragonnier.com',
                  recipients=[f"{data['email']}"])
    msg.html = email_content
    mail.send(msg)

    return 'yaessss worked'


if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists(os.path.join(basedir, "mydatabase.db")):
            db.create_all()

    app.run(debug=True)
