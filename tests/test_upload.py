"""Upload rules on /ops/upload.

Only docx, pptx and xlsx are accepted (ops.ALLOWED_EXTENSIONS).
"""

import io
import os

import pytest


def post_file(client, filename, content=b"data"):
    return client.post(
        "/ops/upload",
        data={"file": (io.BytesIO(content), filename)},
        content_type="multipart/form-data",
    )


@pytest.mark.parametrize("filename", ["report.docx", "deck.pptx", "sheet.xlsx"])
def test_allowed_extensions_are_stored(client, upload_dir, filename):
    response = post_file(client, filename)
    assert response.status_code == 201
    assert response.get_json()["message"] == "File uploaded successfully"
    assert filename in os.listdir(upload_dir)


@pytest.mark.parametrize(
    "filename", ["notes.txt", "payload.exe", "archive.zip", "script.py", "image.png"]
)
def test_unsupported_extensions_are_rejected(client, upload_dir, filename):
    response = post_file(client, filename)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid file type"
    assert os.listdir(upload_dir) == []


def test_extension_check_is_case_insensitive(client, upload_dir):
    assert post_file(client, "Report.DOCX").status_code == 201


def test_double_extension_is_judged_on_the_last_one(client, upload_dir):
    """A classic bypass attempt: payload.docx.exe must not be accepted."""
    assert post_file(client, "payload.docx.exe").status_code == 400
    assert os.listdir(upload_dir) == []


def test_missing_file_part_is_rejected(client):
    response = client.post("/ops/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No file part"


def test_empty_filename_is_rejected(client):
    response = post_file(client, "")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No selected file"


def test_path_traversal_in_filename_is_neutralised(client, upload_dir):
    """secure_filename should strip directory components, so the file cannot
    escape the upload folder."""
    response = post_file(client, "../../escaped.docx")
    assert response.status_code == 201
    stored = os.listdir(upload_dir)
    assert stored == ["escaped.docx"]
    assert not os.path.exists(os.path.join(upload_dir, "..", "..", "escaped.docx"))
