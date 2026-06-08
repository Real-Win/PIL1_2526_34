from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db           = SQLAlchemy()
login_manager = LoginManager()
bcrypt        = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.connexion"

    # user_loader à l'intérieur pour éviter l'import circulaire
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes import matching_bp, auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(matching_bp)

    # Création automatique des tables si elles n'existent pas
    with app.app_context():
        db.create_all()

    return app