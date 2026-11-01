"""Bearer-token authentication for the ops role.

/ops/upload previously accepted a file from any caller that could reach the
URL - no token, no session, no check - which contradicted the role separation
the rest of the service enforces. Ops users now exchange their credentials at
/ops/login for a signed token and present it as:

    Authorization: Bearer <token>
"""

import datetime
import functools

import jwt
from flask import current_app, jsonify, request

from app.models import User

TOKEN_TTL_MINUTES = 60


def issue_ops_token(user):
    """Signed token for an authenticated ops user."""
    return jwt.encode(
        {
            "email": user.email,
            "role": "ops",
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(minutes=TOKEN_TTL_MINUTES),
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def _bearer_token():
    """The token from an Authorization header, or None if absent/malformed."""
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def ops_required(view):
    """Allow only a current ops user through.

    The role is checked twice on purpose: once from the token's claims, and
    once against the database, so a token issued to an account that has since
    been removed or changed role stops working immediately rather than at
    expiry.
    """

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        token = _bearer_token()
        if token is None:
            return jsonify({"error": "Authorization required"}), 401

        try:
            claims = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        if claims.get("role") != "ops":
            return jsonify({"error": "Ops access required"}), 403

        if not User.query.filter_by(email=claims.get("email"), role="ops").first():
            return jsonify({"error": "Ops access required"}), 403

        return view(*args, **kwargs)

    return wrapper
