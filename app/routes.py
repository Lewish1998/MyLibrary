from app import app, db
from app.models import User, Book, UserBook
from app.forms import RegistrationForm, LoginForm, UserSettingsForm, AddBook, EditBook, UpdateCurrentlyReadingForm
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
    form = UpdateCurrentlyReadingForm()
    user_books = UserBook.query.filter_by(user_id=current_user.id).all()
    books = Book.query.filter_by(added_by=current_user.id).all()
    return render_template('index.html', books=books, current_user=current_user, user_books=user_books, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data.lower()))
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
        user = User(username=form.username.data.lower(), email=form.email.data)
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
            title=form.title.data.title(),
            description=form.description.data,
            pages=form.pages.data if form.pages.data else None,
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

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    
    form = EditBook(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.description = form.description.data
        book.pages = form.pages.data if form.pages.data else None
        book.isbn = form.isbn.data
        book.added_by = current_user.id
        db.session.commit()
        flash('Book updated', 'success')
        return redirect(url_for('get_books'))

    return render_template('edit_book.html', form=form, book=book)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted', 'success')

    return redirect(url_for('get_books'))

@app.route('/books/<int:book_id>', methods=['GET'])
@login_required
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    already_reading = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if already_reading:
        flash('You are already reading this book', 'info')
    return render_template('book_detail.html', book=book, current_user=current_user, already_reading=already_reading)

@app.route('/start_reading/<int:book_id>', methods=['POST'])
@login_required
def start_reading(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    
    already_reading = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if already_reading:
        flash('You are already reading this book', 'info')
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book.id)
        db.session.add(user_book)
        db.session.commit()
        flash('You have started reading this book', 'success')

    return redirect(url_for('get_books'))

@app.route('/stop_reading/<int:book_id>', methods=['POST'])
@login_required
def stop_reading(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('get_books'))
    
    already_reading = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if already_reading:
        db.session.delete(already_reading)
        db.session.commit()
        flash('Book removed from currently reading', 'success')
    else:
        flash('You are not reading this book', 'info')


    return redirect(url_for('get_books'))

@app.route('/update_page/<int:user_book_id>', methods=['POST'])
@login_required
def update_page(user_book_id):
    user_book = UserBook.query.get_or_404(user_book_id)

    # Ensure the current user is the owner of the UserBook entry
    if user_book.user_id != current_user.id:
        flash("You are not authorized to update this book.", "error")
        return redirect(url_for('index'))
    
    # Update the current page
    current_page = request.form.get('current_page', type=int)
    if current_page is not None: # Doesn't work if no pages input as non mandatory and 0 <= current_page <= user_book.book.pages:
        user_book.current_page = current_page
        db.session.commit()
        flash(f'Updated current page for {user_book.book.title} to {current_page}.', 'success')
    else:
        flash(f'Invalid page number.', 'error')
    
    return redirect(url_for('index'))

@app.route('/toggle_complete/<int:book_id>', methods=['POST'])
@login_required
def toggle_complete(book_id):
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if user_book:
        user_book.complete = not user_book.complete
        db.session.commit()
        flash(f'Book {"complete" if user_book.complete else "restarted"}', 'success')
    else:
        flash('You are not reading this book', 'error')

    return redirect(url_for('index'))