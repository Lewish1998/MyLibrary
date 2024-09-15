from xmlrpc.client import DateTime
from app import db
from sqlalchemy.sql import func
from app import loginManager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(264), nullable=True)
    # created_at = db.Column(DateTime(timezone=True), server_default=func.now()) # Unsure if will work
    # updated_at = db.Column(DateTime(timezone=True), onupdate=func.now()) # Unsure if will work
    password_hash = db.Column(db.String(264), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@loginManager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='books')