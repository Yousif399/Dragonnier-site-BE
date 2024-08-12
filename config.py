from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from datetime import timedelta
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'Login'
# app.config['SESSION_COOKIE_DOMAIN'] = '.onrender.com'
# This is necessary for cross-site cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
# This ensures the cookie is only sent over HTTPS
app.config['SESSION_COOKIE_SECURE'] = True
# Protects the cookie from JavaScript access
app.config['SESSION_COOKIE_HTTPONLY'] = True


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 587  # Use SSL
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')

app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'uploads')


app.config["CLOUDINARY_CLOUD_NAME"] = os.environ.get('CLOUDINARY_CLOUD_NAME')
app.config["CLOUDINARY_API_KEY"] = os.environ.get('CLOUDINARY_API_KEY')
app.config["CLOUDINARY_API_SECRET"] = os.environ.get('CLOUDINARY_API_SECRET')


cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

db = SQLAlchemy(app)
# somethin
