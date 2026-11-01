"""Authentication on /ops/upload.

The endpoint previously accepted a file from anyone who could reach the URL.
These tests pin the gap shut: a caller must present a bearer token issued by
/ops/login to an account that is still an ops user.
"""

import datetime
import io

import jwt
import pytest

TEST_SECRET = "test-secret-not-the-deployed-one"


def post_file(client, headers=None):
    return client.post(
        "/ops/upload",
        data={"file": (io.BytesIO(b"data"), "report.docx")},
        content_type="multipart/form-data",
        headers=headers or {},
    )


def test_login_returns_a_token(client, make_user):
    make_user("ops@example.com", role="ops")
    response = client.post(
        "/ops/login", json={"email": "ops@example.com", "password": "pw-12345"}
    )
    assert response.status_code == 200
    assert response.get_json()["token"]


def test_upload_without_a_token_is_refused(client, upload_dir):
    """The original hole: no credentials at all."""
    import os

    response = post_file(client)
    assert response.status_code == 401
    assert response.get_json()["error"] == "Authorization required"
    assert os.listdir(upload_dir) == []


@pytest.mark.parametrize(
    "header",
    [
        {"Authorization": "Bearer"},
        {"Authorization": "Bearer "},
        {"Authorization": "token abc123"},
        {"Authorization": "abc123"},
    ],
)
def test_malformed_authorization_headers_are_refused(client, header):
    assert post_file(client, header).status_code == 401


def test_token_from_login_is_accepted(client, make_user):
    """End to end: credentials in, token out, upload accepted."""
    make_user("staff@example.com", role="ops")
    login = client.post(
        "/ops/login", json={"email": "staff@example.com", "password": "pw-12345"}
    )
    token = login.get_json()["token"]

    response = post_file(client, {"Authorization": f"Bearer {token}"})
    assert response.status_code == 201


def test_client_token_cannot_upload(client, make_user):
    """A client account must not be able to mint its way into ops."""
    make_user("customer@example.com", role="client")
    token = jwt.encode(
        {
            "email": "customer@example.com",
            "role": "client",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        TEST_SECRET,
        algorithm="HS256",
    )
    response = post_file(client, {"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.get_json()["error"] == "Ops access required"


def test_role_claim_cannot_be_forged_against_a_client_account(client, make_user):
    """Claiming role=ops in the token is not enough; the account is rechecked."""
    make_user("sneaky@example.com", role="client")
    token = jwt.encode(
        {
            "email": "sneaky@example.com",
            "role": "ops",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        TEST_SECRET,
        algorithm="HS256",
    )
    assert post_file(client, {"Authorization": f"Bearer {token}"}).status_code == 403


def test_token_signed_with_another_secret_is_refused(client, make_user):
    make_user("ops2@example.com", role="ops")
    forged = jwt.encode(
        {
            "email": "ops2@example.com",
            "role": "ops",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        },
        "not-the-app-secret",
        algorithm="HS256",
    )
    response = post_file(client, {"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid token"


def test_expired_token_is_refused(client, make_user, token_for):
    make_user("ops3@example.com", role="ops")
    expired = token_for(
        {"email": "ops3@example.com", "role": "ops"}, expires_in_minutes=-1
    )
    response = post_file(client, {"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.get_json()["error"] == "Token expired"


def test_token_stops_working_when_the_account_is_removed(client, make_user, app):
    """Revocation: the database is consulted on every request, so a deleted
    account cannot keep uploading until its token expires."""
    from app.extensions import db

    user = make_user("temp@example.com", role="ops")
    login = client.post(
        "/ops/login", json={"email": "temp@example.com", "password": "pw-12345"}
    )
    headers = {"Authorization": f"Bearer {login.get_json()['token']}"}
    assert post_file(client, headers).status_code == 201

    db.session.delete(user)
    db.session.commit()

    assert post_file(client, headers).status_code == 403
