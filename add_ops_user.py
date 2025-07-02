from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "ops@example.com"
    password = "pass123"
    role = "ops"

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print("✅ Ops user already exists.")
    else:
        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password, role=role, is_verified=True)
        db.session.add(user)
        db.session.commit()
        print("✅ Ops user created successfully.")
