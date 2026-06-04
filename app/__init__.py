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
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Page de redirection si non connecté
    login_manager.login_view = 'auth.login'
    
    # Enregistrement des blueprints
    from app.routes import auth, main
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    return app