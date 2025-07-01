from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.extensions import db
import jwt
import os

client_bp = Blueprint('client_bp', __name__)
UPLOAD_FOLDER = 'uploaded_files'

@client_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 409
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, role='client', is_verified=False)
    db.session.add(new_user)
    db.session.commit()
    token = jwt.encode({"email": email}, current_app.config['SECRET_KEY'], algorithm="HS256")
    if isinstance(token, bytes): token = token.decode('utf-8')
    verify_link = f"http://127.0.0.1:5000/client/verify/{token}"
    return jsonify({"message": "Client registered successfully. Verify your email.", "verify_link": verify_link}), 201

@client_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        email = decoded.get('email')
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user.is_verified:
            return jsonify({"message": "Email already verified"}), 200
        user.is_verified = True
        db.session.commit()
        return jsonify({"message": "Email verified successfully!"}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Verification link expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 400

@client_bp.route('/login', methods=['POST'])
def client_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email, role='client').first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403
    return jsonify({"message": "Login successful"}), 200

@client_bp.route('/files', methods=['GET'])
def list_files():
    user_email = request.args.get('email')
    user = User.query.filter_by(email=user_email, role='client', is_verified=True).first()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({"files": files}), 200

@client_bp.route('/download-file/<filename>', methods=['GET'])
def generate_download_link(filename):
    user_email = request.args.get('email')
    user = User.query.filter_by(email=user_email, role='client', is_verified=True).first()
    if not user:
        return jsonify({"error": "Unauthorized"}), 403
    token = jwt.encode({"filename": filename, "email": user.email}, current_app.config['SECRET_KEY'], algorithm="HS256")
    if isinstance(token, bytes): token = token.decode('utf-8')
    secure_url = f"http://127.0.0.1:5000/client/download/{token}"
    return jsonify({"download-link": secure_url, "message": "success"}), 200

@client_bp.route('/download/<token>', methods=['GET'])
def secure_download(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        filename = data['filename']
        email = data['email']
        user = User.query.filter_by(email=email, role='client', is_verified=True).first()
        if not user:
            return jsonify({"error": "Unauthorized"}), 403
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid or expired link"}), 400
