from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from config import Config

db            = SQLAlchemy()
login_manager = LoginManager()
bcrypt        = Bcrypt()
socketio      = SocketIO()          # ← nouveau


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")   # ← nouveau

    login_manager.login_view = "auth.connexion"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from app.routes import matching_bp, auth_bp
    from app.routes_messagerie import messagerie_bp   # ← nouveau

    app.register_blueprint(auth_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(messagerie_bp)             # ← nouveau

    with app.app_context():
        db.create_all()

    return app