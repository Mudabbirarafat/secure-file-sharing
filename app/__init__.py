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
    return app
