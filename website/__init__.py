from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os, random

db = SQLAlchemy()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # absolute path of this folder
DB_NAME = os.path.join(BASE_DIR, 'database.db')

def create_app():
    app = Flask(__name__)
    random.seed(0)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    print("Using DB:", DB_NAME)
    db.init_app(app)

    # Import blueprints
    from .views import views
    from .prediction import prediction
    from .messages import messages
    from .auth import auth

    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(prediction, url_prefix='/')
    app.register_blueprint(messages, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import all models here to register with SQLAlchemy before creating tables
    from .models import Messages, User, Prediction

    create_database(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_database(app):
    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all()   # <-- Corrected here, no app=app argument
            print("Created Database!")
