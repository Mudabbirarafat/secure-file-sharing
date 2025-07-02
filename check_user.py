from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='ops@example.com').first()
    if user:
        print(f"✅ Found user: {user.email} | Role: {user.role} | Verified: {user.is_verified}")
    else:
        print("❌ Ops user does not exist.")
