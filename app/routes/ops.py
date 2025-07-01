from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import User
from app.extensions import db
import os

ops_bp = Blueprint('ops_bp', __name__)
UPLOAD_FOLDER = 'uploaded_files'
ALLOWED_EXTENSIONS = {'docx', 'pptx', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ops_bp.route('/login', methods=['POST'])
def ops_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    user = User.query.filter_by(email=email, role='ops').first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"message": "Ops login successful"}), 200

@ops_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"message": "File uploaded successfully"}), 201
    return jsonify({"error": "Invalid file type"}), 400
