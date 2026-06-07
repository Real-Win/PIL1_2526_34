from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)        # ← décommenté
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.connexion'   # ← décommenté

    from app.routes import matching_bp, auth_bp
    app.register_blueprint(matching_bp)
    app.register_blueprint(auth_bp)

    return app