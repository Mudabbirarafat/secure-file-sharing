"""Signup, email verification and login."""

import datetime

import jwt

from app.models import User


def test_signup_creates_an_unverified_client(client, app):
    response = client.post(
        "/client/signup", json={"email": "new@example.com", "password": "pw-12345"}
    )
    assert response.status_code == 201
    assert "verify_link" in response.get_json()

    user = User.query.filter_by(email="new@example.com").first()
    assert user is not None
    assert user.role == "client"
    assert user.is_verified is False


def test_signup_stores_a_hash_not_the_password(client, app):
    client.post(
        "/client/signup", json={"email": "hash@example.com", "password": "pw-12345"}
    )
    user = User.query.filter_by(email="hash@example.com").first()
    assert user.password != "pw-12345"
    assert user.password.startswith(("pbkdf2:", "scrypt:"))


def test_signup_requires_email_and_password(client):
    assert client.post("/client/signup", json={"email": "a@b.com"}).status_code == 400
    assert client.post("/client/signup", json={"password": "x"}).status_code == 400


def test_duplicate_signup_is_rejected(client):
    payload = {"email": "dupe@example.com", "password": "pw-12345"}
    assert client.post("/client/signup", json=payload).status_code == 201
    second = client.post("/client/signup", json=payload)
    assert second.status_code == 409
    assert second.get_json()["error"] == "User already exists"


def test_verification_marks_the_user_verified(client, token_for):
    client.post(
        "/client/signup", json={"email": "verify@example.com", "password": "pw-12345"}
    )
    token = token_for({"email": "verify@example.com"}, expires_in_minutes=30)

    response = client.get(f"/client/verify/{token}")
    assert response.status_code == 200
    assert User.query.filter_by(email="verify@example.com").first().is_verified is True


def test_expired_verification_link_is_refused(client, token_for):
    client.post(
        "/client/signup", json={"email": "stale@example.com", "password": "pw-12345"}
    )
    expired = token_for({"email": "stale@example.com"}, expires_in_minutes=-1)

    response = client.get(f"/client/verify/{expired}")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Verification link expired"
    assert User.query.filter_by(email="stale@example.com").first().is_verified is False


def test_verification_token_signed_with_another_key_is_refused(client):
    """A token minted with a different secret must not verify an account."""
    forged = jwt.encode(
        {
            "email": "forged@example.com",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        "a-different-secret",
        algorithm="HS256",
    )
    response = client.get(f"/client/verify/{forged}")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid token"


def test_login_requires_verification(client, make_user):
    make_user("unverified@example.com", is_verified=False)
    response = client.post(
        "/client/login",
        json={"email": "unverified@example.com", "password": "pw-12345"},
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "Email not verified"


def test_login_succeeds_once_verified(client, make_user):
    make_user("ok@example.com")
    response = client.post(
        "/client/login", json={"email": "ok@example.com", "password": "pw-12345"}
    )
    assert response.status_code == 200


def test_login_rejects_a_wrong_password(client, make_user):
    make_user("pw@example.com")
    response = client.post(
        "/client/login", json={"email": "pw@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_ops_account_cannot_log_in_through_the_client_route(client, make_user):
    """The two roles have separate login endpoints and must not cross over."""
    make_user("staff@example.com", role="ops")
    response = client.post(
        "/client/login", json={"email": "staff@example.com", "password": "pw-12345"}
    )
    assert response.status_code == 401


def test_client_account_cannot_log_in_through_the_ops_route(client, make_user):
    make_user("customer@example.com", role="client")
    response = client.post(
        "/ops/login", json={"email": "customer@example.com", "password": "pw-12345"}
    )
    assert response.status_code == 401
