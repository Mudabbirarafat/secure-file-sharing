import os


def upload_folder():
    """Absolute path of the directory uploaded files live in.

    Always absolute, and resolved on every call so it follows the process
    working directory.

    This matters because the two sides of the feature resolve relative paths
    differently: os.listdir() resolves against the working directory, while
    Flask's send_from_directory() resolves against app.root_path. Passing the
    bare string 'uploaded_files' to both means the listing endpoint and the
    download endpoint can silently point at different folders, so a client
    sees a file it cannot fetch.

    Override with the UPLOAD_FOLDER environment variable, which is also how a
    deployment can point this at a mounted disk.
    """
    path = os.path.abspath(os.environ.get("UPLOAD_FOLDER", "uploaded_files"))
    os.makedirs(path, exist_ok=True)
    return path
