"""Signed download links, listing, and the service index.

The security claim this project makes is that downloads go through a signed,
expiring link tied to a verified client. These tests hold it to that.
"""

import os

import pytest


@pytest.fixture
def stored_file(upload_dir):
    path = os.path.join(upload_dir, "report.docx")
    with open(path, "wb") as fh:
        fh.write(b"confidential")
    return "report.docx"


def test_index_lists_the_api(client):
    """Without this route the deployed service answers / with a bare 404."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_json()
    assert body["service"] == "secure-file-sharing"
    assert "client" in body["endpoints"] and "ops" in body["endpoints"]


def test_verified_client_sees_the_file_list(client, make_user, stored_file):
    make_user("reader@example.com")
    response = client.get("/client/files?email=reader@example.com")
    assert response.status_code == 200
    assert stored_file in response.get_json()["files"]


def test_unverified_client_cannot_list_files(client, make_user):
    make_user("pending@example.com", is_verified=False)
    response = client.get("/client/files?email=pending@example.com")
    assert response.status_code == 403


def test_unknown_email_cannot_list_files(client):
    assert client.get("/client/files?email=nobody@example.com").status_code == 403


def test_ops_user_cannot_list_client_files(client, make_user, stored_file):
    """Ops upload files; the listing endpoint is for clients only."""
    make_user("ops@example.com", role="ops")
    response = client.get("/client/files?email=ops@example.com")
    assert response.status_code == 403


def test_download_link_is_issued_to_a_verified_client(client, make_user, stored_file):
    make_user("dl@example.com")
    response = client.get(f"/client/download-file/{stored_file}?email=dl@example.com")
    assert response.status_code == 200
    assert "download-link" in response.get_json()


def test_download_link_is_refused_to_an_unverified_client(client, make_user, stored_file):
    make_user("nope@example.com", is_verified=False)
    response = client.get(f"/client/download-file/{stored_file}?email=nope@example.com")
    assert response.status_code == 403


def test_signed_link_returns_the_file(client, make_user, stored_file, token_for):
    make_user("fetch@example.com")
    token = token_for({"filename": stored_file, "email": "fetch@example.com"})
    response = client.get(f"/client/download/{token}")
    assert response.status_code == 200
    assert response.data == b"confidential"


def test_expired_signed_link_is_refused(client, make_user, stored_file, token_for):
    make_user("late@example.com")
    expired = token_for(
        {"filename": stored_file, "email": "late@example.com"}, expires_in_minutes=-1
    )
    response = client.get(f"/client/download/{expired}")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Download link expired"


def test_tampered_signed_link_is_refused(client, make_user, stored_file, token_for):
    make_user("tamper@example.com")
    token = token_for({"filename": stored_file, "email": "tamper@example.com"})
    response = client.get(f"/client/download/{token}x")
    assert response.status_code == 400


def test_link_for_a_deleted_account_stops_working(
    client, make_user, stored_file, token_for, app
):
    """A link remains valid for 15 minutes, but the holder must still be a
    verified client at the moment of download."""
    from app.extensions import db

    user = make_user("gone@example.com")
    token = token_for({"filename": stored_file, "email": "gone@example.com"})

    db.session.delete(user)
    db.session.commit()

    response = client.get(f"/client/download/{token}")
    assert response.status_code == 403
