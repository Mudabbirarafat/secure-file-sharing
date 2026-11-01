"""Shared fixtures.

Two things need isolating from the developer's machine:

* the database - app/config.py hardcodes sqlite:///data.db, so every fixture
  points SQLALCHEMY_DATABASE_URI at a throwaway file first;
* the upload directory - UPLOAD_FOLDER is the relative path 'uploaded_files',
  resolved against the current working directory at call time, so the tests
  chdir into a tmp_path and the real one is never touched.
"""

import datetime
import os

import jwt
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User

TEST_SECRET = "test-secret-not-the-deployed-one"


@pytest.fixture
def app(tmp_path, monkeypatch):
    # Run inside a scratch directory so uploaded_files/ and the sqlite file
    # are created there and discarded with the test.
    monkeypatch.chdir(tmp_path)
    os.makedirs("uploaded_files", exist_ok=True)

    application = create_app()
    application.config.update(
        TESTING=True,
        SECRET_KEY=TEST_SECRET,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    """Insert a user directly, bypassing signup, so tests can set role and
    verification state without going through the whole flow."""

    def _make(email, password="pw-12345", role="client", is_verified=True):
        user = User(
            email=email,
            password=generate_password_hash(password),
            role=role,
            is_verified=is_verified,
        )
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def token_for():
    """Mint a JWT with the same secret the app uses under test, so expiry and
    tampering can be exercised without waiting."""

    def _token(payload, expires_in_minutes=15):
        body = dict(payload)
        body["exp"] = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=expires_in_minutes
        )
        return jwt.encode(body, TEST_SECRET, algorithm="HS256")

    return _token


@pytest.fixture
def upload_dir(app):
    """Path of the upload folder for the current test."""
    return os.path.join(os.getcwd(), "uploaded_files")


@pytest.fixture
def ops_headers(app, make_user):
    """Authorization header for a signed-in ops user.

    /ops/upload requires one; without it the endpoint would accept a file from
    any caller that could reach the URL.
    """
    from app.auth import issue_ops_token

    user = make_user("uploader@example.com", role="ops")
    return {"Authorization": f"Bearer {issue_ops_token(user)}"}
