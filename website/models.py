from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  


class Messages(db.Model):
    __tablename__ = "messages"  # nom de table explicite

    """model for stocking the messages from contact us"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    messages = db.Column(db.String(10000))

    def __str__(self):
        return self.name
	

class User(db.Model, UserMixin):
    __tablename__ = "users"  # nom de table explicite, au pluriel par convention

    """Model for storing registered users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Hash and set the password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify the provided password against the stored hash."""
        return check_password_hash(self.password, password)
    
class Prediction(db.Model):
    __tablename__ = "predictions"  # nom de table explicite au pluriel

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    disease_type = db.Column(db.String(50), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    prediction_result = db.Column(db.Integer, nullable=False)  # ou Float si nécessaire
    original_message = db.Column(db.Text, nullable=True)
    reworded_message = db.Column(db.Text, nullable=True)
    user_identifier = db.Column(db.String(100), nullable=True)
