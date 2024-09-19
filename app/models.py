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
    email = db.Column(db.String(100), nullable=False, unique=True)
    bio = db.Column(db.String(264), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now()) 
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now()) 
    password_hash = db.Column(db.String(264), nullable=False)

    user_books = db.relationship('UserBook', back_populates='user')
    completed_books = db.relationship('CompletedBook', back_populates='user')

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
    description = db.Column(db.Text, nullable=True)
    pages = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(13), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=True)
    added = db.Column(db.DateTime(timezone=True), server_default=func.now())
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Relationships
    author = db.relationship('Author', back_populates='books')
    genre = db.relationship('Genre', back_populates='books')
    user_books = db.relationship('UserBook', back_populates='book')

    completed_books = db.relationship('CompletedBook', back_populates='book')

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Relationship to books
    books = db.relationship('Book', back_populates='genre')

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Relationship to books
    books = db.relationship('Book', back_populates='author')


class UserBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_started = db.Column(db.DateTime(timezone=True), server_default=func.now())
    current_page = db.Column(db.Integer, nullable=False, default=0)
    complete = db.Column(db.Boolean, default=False)
    # Relationships
    user = db.relationship('User', back_populates='user_books')
    book = db.relationship('Book', back_populates='user_books')
    reading_logs = db.relationship('ReadingLog', back_populates='user_book', cascade="all, delete-orphan")

class CompletedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_completed = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = db.relationship('User', back_populates='completed_books')
    book = db.relationship('Book', back_populates='completed_books')

class ReadingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_book_id = db.Column(db.Integer, db.ForeignKey('user_book.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    pages_read = db.Column(db.Integer, nullable=False)

    user_book = db.relationship('UserBook', back_populates='reading_logs')