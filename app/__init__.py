from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from config import Config
import os

db            = SQLAlchemy()
login_manager = LoginManager()
bcrypt        = Bcrypt()
socketio      = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = "auth.connexion"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Route pour servir les fichiers uploadés
    @app.route('/static/uploads/<filename>')
    def uploaded_file(filename):
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        return send_from_directory(upload_folder, filename)

    # Blueprints
    from app.routes import matching_bp, auth_bp
    from app.routes_messagerie import messagerie_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(messagerie_bp)

    with app.app_context():
        db.create_all()

    return app