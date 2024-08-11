from flask import request, json, jsonify, render_template, send_file, send_from_directory, redirect, url_for, session
from config import app, db
from models import Product
from flask_mail import Mail, Message
import os
import ssl
from werkzeug.utils import secure_filename
import uuid
import cloudinary.uploader
import requests

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
            unique_filename = make_unique_filename(filename)

            upload_result = cloudinary.uploader.upload(
                product_file, public_id=unique_filename)
            print('result uploader: ', upload_result)
            product_img = upload_result['secure_url']

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


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     print('kkk', filename)
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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

        # deleteing the img  from file
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"Deleted image file: {img_path}")
        else:
            print(f"img file not founded: {img_path}")

        return jsonify({"Message": "Product was deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Message": f"sn error occured: {str(e)}"}), 500


# send email functions
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


def validate_email(email):
    # url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={os.environ.get('ZeroBounce_API_KEY')}"
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={os.environ.get('ZeroBounce_API_KEY')}"

    try:
        response = requests.get(url)
        data = response.json()
        if data and 'data' in data and 'status' in data['data']:
            print('status of the email: ', data['data']['status'])
            if data['data']['status'] == 'invalid' or data['data']['status'] == 'disposable':
                return False
        else:
            print('No data founded ')
            return False

        return True

    except Exception as e:
        print('Error occurred ', e)
        return False


@app.route('/place-order', methods=['POST'])
def place_order():
    # order = process_order(request.form)
    data = request.json
    recipient = data['email']
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
                <div class="total"><strong>Total:</strong> {data['total']}</div>
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
    email_content2 = f"""
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
            <h2>An order have been submitted by, {data['name']}!</h2>
        </div>
            <div class="order-details">
                <h3>Order Details:</h3>
                <div><strong>Product:</strong> {data['product']}</div>
                <div><strong>Quantity:</strong> {data['quantity']}</div>
                <div><strong>Subtotal:</strong> {data['subtotal']}</div>
                <div><strong>Taxes:</strong> {data['taxes']}</div>
                <div class="total"><strong>Total:</strong> {data['total']}</div>
            </div>
            <div class="shipping-info">
                <h3>Shipping Information:</h3>
                <div><strong>Name:</strong> {data['name']}</div>
                <div><strong>Email:</strong> {recipient}</div>
                <div><strong>Address:</strong> {data['address']}</div>
                <div><strong>City:</strong> {data['city']}</div>
                <div><strong>Postal Code:</strong> {data['postalCode']}</div>
                <div><strong>Phone Number:</strong> {data['phone']}</div>
                <div><strong>Company:</strong> {data['company']}</div>
            </div>
        </div>
    </body>
    </html>
    """

    if validate_email(recipient) == True:
        print('Email is valid')
        send_confirmation(email_content, recipient)
        send_notification(email_content2, recipient)
        return jsonify({"message": "Order was placed successfully"}), 200
    else:
        print('Email entered was not valid')
        return jsonify({"Message": "Email entered was not valid"}), 400


# @app.route('/open', methods=["GET"])
# def open_app():
#     print('redirecting to dragonnier')
#     return redirect('http://127.0.0.1:5500/access-product.html')

username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')

@app.route('/login', methods=["POST"])
def log_in():
    print('login is processing')
    if request.method == "POST":
        incoming_username = request.form['username']
        incoming_password = request.form['password']

        if incoming_username == username and incoming_password == password:
            session.permanent = True
            session['authenticated'] = True
            return jsonify({'Message': f"Routing is working {username, password}"}), 200
        else:
            return jsonify({'Message': 'Invalid credentials'}), 401

    return jsonify({"Message": "Should go back to log-in "}) 

    
    
    # return jsonify({"Message": f"The user: {username}  is not found, or {password} is wrong password make sure you entered a valid information "}), 401


@app.route('/logout', methods=["GET"])
def log_out():
    # print(session.get('authenticated'))
    if 'authenticated' in session:
        session.pop('authenticated', False)
        return jsonify({"Message": "User has been logged out"}), 200
    else:
        print('no session found')
    return jsonify({"Message": "An error occur"}), 403


@app.route('/handle-product', methods=['GET'])
def handle_product_page():

    if session.get('authenticated'):
        print('its working')
        print(session['authenticated'])
        return jsonify({"Message": "worked"}), 200
    else:
        print("no user found")
        return jsonify({"Message": "not worked"}), 401


# @app.route("/login1", methods=["POST", "GET"])
# def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        session["user"] = username
        session.permanent = True

        print(f"User is {username},  session is {session}")
        session.modified = True
        return jsonify({"Message": "worked"}), 200
    else:
        if "user" in session:
            return jsonify({"Message": "Session has been set and has a value now"}), 200 or 201

    return jsonify({"Message": "No session available check server or try again"}), 401


# @app.route("/user")
# def user():
#     print(f"session is {session}")
#     if "user" in session:
#         user = session["user"]
#         print(user)
#         return f"<h1>{user}</h1>"
#     else:
#         print('No user in session.....')
#         return "No user in session found error", 401


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
