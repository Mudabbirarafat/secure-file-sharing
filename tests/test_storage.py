"""Regression test for the upload directory resolving two different ways.

os.listdir() resolves a relative path against the working directory; Flask's
send_from_directory() resolves it against app.root_path. While both routes
passed the bare string 'uploaded_files', a client could list a file and then
get a 404 downloading it whenever those two directories differed - which is
any deployment not started from the repository root.

app.storage.upload_folder() returns one absolute path for both.
"""

import os

from app.storage import upload_folder


def test_upload_folder_is_absolute(app):
    assert os.path.isabs(upload_folder())


def test_upload_folder_follows_the_working_directory(app, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert upload_folder() == os.path.join(str(tmp_path), "uploaded_files")


def test_upload_folder_is_created_if_missing(app, tmp_path, monkeypatch):
    target = tmp_path / "fresh"
    target.mkdir()
    monkeypatch.chdir(target)
    assert not (target / "uploaded_files").exists()
    assert os.path.isdir(upload_folder())


def test_upload_folder_honours_the_environment_override(app, tmp_path, monkeypatch):
    """A deployment points this at a mounted disk."""
    custom = tmp_path / "mounted-disk"
    monkeypatch.setenv("UPLOAD_FOLDER", str(custom))
    assert upload_folder() == str(custom)
    assert custom.is_dir()


def test_uploaded_file_is_listed_and_downloadable(client, make_user, ops_headers):
    """The end-to-end invariant the bug broke: anything the listing shows must
    be fetchable through a signed link."""
    import io

    upload = client.post(
        "/ops/upload",
        data={"file": (io.BytesIO(b"payload"), "agreement.docx")},
        content_type="multipart/form-data",
        headers=ops_headers,
    )
    assert upload.status_code == 201

    make_user("both@example.com")
    listing = client.get("/client/files?email=both@example.com")
    assert "agreement.docx" in listing.get_json()["files"]

    link = client.get("/client/download-file/agreement.docx?email=both@example.com")
    token = link.get_json()["download-link"].rsplit("/", 1)[1]

    download = client.get(f"/client/download/{token}")
    assert download.status_code == 200
    assert download.data == b"payload"
