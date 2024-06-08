from flask import request, json, jsonify, render_template, send_file, send_from_directory
from config import app, db
from models import Product
from flask_mail import Mail, Message
import os
import ssl
from werkzeug.utils import secure_filename
import uuid


# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # Ensure correct path

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
def make_unique_filename(filename):
    new_filename = str(uuid.uuid4()) + '_' + filename
    print(new_filename)
    return new_filename


@app.route('/create-product', methods=['POST'])
def create_products():

    try:
        product_name = request.form["productName"]
        product_price = request.form["productPrice"]
        product_quantity = request.form["productQuantity"]
        product_img = request.form.get("productImg", None)
        product_file = request.files.get("productFile", None)

        print("Product Name:", product_name)
        print("Product Price:", product_price)
        print("Product Quantity:", product_quantity)
        print("Product Img URL:", product_img)
        print("Product Img File:", product_file)

        if product_file:
            filename = secure_filename(product_file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            destination_path = os.path.join(
                app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(destination_path):
                filename = make_unique_filename(filename)
                destination_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename)

            product_file.save(destination_path)
            product_img = filename

        new_product = Product(product_name=product_name,
                              product_price=product_price,
                              product_img=product_img,
                              product_quantity=product_quantity)
        try:
            db.session.add(new_product)
            db.session.commit()
            return jsonify({"Message": "Product created"}), 201
        except Exception as ex:
            return jsonify({"Message": str(ex)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print('kkk',filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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
    
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], product.product_img)
    try:
        db.session.delete(product)
        db.session.commit()

        #deleteing the img  from file 
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"Deleted image file: {img_path}")
        else:
            print(f"img file not founded: {img_path}")
        
        return jsonify({"Message": "Product was deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Message": f"sn error occured: {str(e)}"}),500




#send email functions 
mail = Mail(app)


def send_confirmation(email_content, recipient):
    msg = Message(subject='Order Confirmation', sender='help@dragonnier.com',
                  recipients=[f"{recipient}"])
    msg.html = email_content
    mail.send(msg)


def send_notification(email_content, recipient):
    msg = Message(subject='Order Confirmation', sender='help@dragonnier.com',
                  recipients=[f"{'help@dragonnier.com'}"])
    msg.html = email_content
    mail.send(msg)


ssl._create_default_https_context = ssl._create_unverified_context


# @app.route('/image')
# def serve_image():
#     image_path = 'images/DragonnierLogo.png'
#     return send_file(image_path, mimetype='image/jpeg')


@app.route('/place-order', methods=['POST'])
def place_order():
    # order = process_order(request.form)
    data = request.json

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

            .email {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
        <div class="input-wrapper">
         <img src="https://dragonnier-site.netlify.app/images/DragonnierLogo.png" alt="Logo" width="60">
            <h2>Thank You for Your Order, {data['name']}!</h2>
        </div>
            <div class="order-details">
                <h3>Order Details:</h3>
                <div><strong>Product:</strong> {data['product']}</div>
                <div><strong>Quantity:</strong> {data['quantity']}</div>
                <div><strong>Subtotal:</strong> {data['subtotal']}</div>
                <div><strong>Taxes:</strong> {data['taxes']}</div>
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
            <h3>Your order is now being processed. If you have any questions or need to make changes to your order, please feel free to contact us at <a class="email" href="mailto:help@dragonnier.com">help@dragonnier.com.</a> </h3>
        </div>
    </body>
    </html>
    """
    recipient = data['email']

    send_confirmation(email_content, recipient)
    # send_notification(email_content,recipient)

    return 'yaessss worked'


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
