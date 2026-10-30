from flask import Flask
from app.extensions import db
from app.routes.client import client_bp
from app.routes.ops import ops_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)

    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(ops_bp, url_prefix="/ops")

    @app.route("/")
    def index():
        """Service index. The API is JSON-only, so without this the root
        path returns a bare 404 and the service looks down."""
        return {
            "service": "secure-file-sharing",
            "status": "ok",
            "docs": "https://github.com/Mudabbirarafat/secure-file-sharing",
            "endpoints": {
                "client": [
                    "POST /client/signup",
                    "GET  /client/verify/<token>",
                    "POST /client/login",
                    "GET  /client/files",
                    "GET  /client/download-file/<filename>",
                    "GET  /client/download/<token>",
                ],
                "ops": [
                    "POST /ops/login",
                    "POST /ops/upload",
                ],
            },
        }

    return app
