from app import app, db
from app.models import User, Book
from app.forms import RegistrationForm, LoginForm, UserSettingsForm, AddBook, EditBook
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as sa
import requests
import os
import dotenv
from flask import request, jsonify

dotenv.load_dotenv()
email = os.environ.get('EMAIL')

@app.route('/')
@login_required
def index():
    books = Book.query.all()
    return render_template('index.html', books=books, current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.errorhandler(404)
def not_found(err):
    return render_template('404.html')

@app.route('/user-settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm(obj=current_user)

    if form.validate_on_submit():
        # Check if username has changed
        if form.username.data != current_user.username:
            current_user.username = form.username.data
        
        # Handle password change
        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        # Update the user if any field has changed
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user_settings'))

    return render_template('user_settings.html', form=form)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBook()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            description=form.description.data,
            pages=form.pages.data,
            isbn=form.isbn.data,
            added_by=current_user.id
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added.')
        return redirect(url_for('get_books'))
    return render_template('add_book.html', form=form)

@app.route('/books', methods=['GET', 'POST'])
@login_required
def get_books():
    books = Book.query.all()
    users = User.query.all()
    return render_template('books.html', books=books, current_user=current_user, users=users)

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get(id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    
    form = EditBook(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.description = form.description.data
        book.pages = form.pages.data
        book.isbn = form.isbn.data
        book.added_by = current_user.id
        db.session.commit()
        flash('Book updated', 'success')
        return redirect(url_for('get_books'))

    return render_template('edit_book.html', form=form, book=book)

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted', 'success')

    return redirect(url_for('get_books'))
