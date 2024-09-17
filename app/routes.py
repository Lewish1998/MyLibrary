from app import app, db
from app.models import User, Book
from app.forms import RegistrationForm, LoginForm, UserSettingsForm, SearchBook, AddBook
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
    # users = User.query.all()
    return render_template('index.html') #users=users, books=books)

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
        return redirect(url_for('add_book'))
    return render_template('add_book.html', form=form)

@app.route('/books', methods=['GET', 'POST'])
@login_required
def get_books():
    books = Book.query.all()
    return render_template('books.html', books=books, current_user=current_user)



# # Not using these either... No API for you
# @app.route('/search', methods=['GET', 'POST'])
# @login_required
# def search():
#     form = SearchBook()
#     if form.validate_on_submit():
#         book = requests.get('https://openlibrary.org/search.json?q=the+lord+of+the+rings')
#         return book.json()#url_for('search', book=book)
#     return render_template('search.html', form=form)


# @app.route('/test', methods=['GET', 'POST'])
# @login_required
# def test():
#     if request.is_json:  # Ensure request contains JSON
#         isbn = request.json.get('isbn')

#         # Fetch book data using ISBN
#         response = requests.get(f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data')
        
#         if response.status_code == 200:
#             book_data = response.json()
#             if book_data:
#                 return jsonify(book_data)
#             else:
#                 return jsonify({'error': 'No data found for the provided ISBN'}), 404
#         else:
#             return jsonify({'error': 'Book not found'}), 404
#     else:
#         return jsonify({'error': 'Unsupported media type, please send JSON'}), 415


#     # isbn = 1526617161
#     # api_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
#     # headers = {
#     #     "User-Agent": "MyLibrary/1.0 ({email})"
#     # }
#     # response = requests.get(api_url, headers=headers)
    
#     if response.status_code == 200:
#         book_data = response.json()
#         if f'ISBN:{isbn}' in book_data:
#             book_info = book_data[f'ISBN:{isbn}']
#             book = {
#                 'title': book_info.get('title'),
#                 'description': book_info.get('notes'),
#                 'pages': book_info.get('number_of_pages'),
#                 'isbn': isbn,
#                 'author': ', '.join([author['name'] for author in book_info.get('authors', [])]),
#                 'genre': book_info.get('subjects', [{'name': 'Unknown'}])[0]['name']
#             }

#     return render_template('test.html', book=book, email=email)





















# # CRUD Operations for Users
# @app.route('/user/new', methods=['GET', 'POST'])
# def new_user():
#     form = UserForm()
#     if form.validate_on_submit():
#         user = User(name=form.name.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('User created successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('user_form.html', form=form)

# @app.route('/user/<int:id>/edit', methods=['GET', 'POST'])
# def edit_user(id):
#     user = User.query.get_or_404(id)
#     form = UserForm(obj=user)
#     if form.validate_on_submit():
#         user.name = form.name.data
#         db.session.commit()
#         flash('User updated successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('user_form.html', form=form)

# @app.route('/user/<int:id>/delete', methods=['POST'])
# def delete_user(id):
#     user = User.query.get_or_404(id)
#     db.session.delete(user)
#     db.session.commit()
#     flash('User deleted successfully!', 'success')
#     return redirect(url_for('index'))

# # CRUD Operations for Books
# @app.route('/book/new', methods=['GET', 'POST'])
# def new_book():
#     form = BookForm()
#     if form.validate_on_submit():
#         book = Book(title=form.title.data, author=form.author.data, user_id=form.user_id.data)
#         db.session.add(book)
#         db.session.commit()
#         flash('Book created successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('book_form.html', form=form)

# @app.route('/book/<int:id>/edit', methods=['GET', 'POST'])
# def edit_book(id):
#     book = Book.query.get_or_404(id)
#     form = BookForm(obj=book)
#     if form.validate_on_submit():
#         book.title = form.title.data
#         book.author = form.author.data
#         book.user_id = form.user_id.data
#         db.session.commit()
#         flash('Book updated successfully!', 'success')
#         return redirect(url_for('index'))
#     return render_template('book_form.html', form=form)

# @app.route('/book/<int:id>/delete', methods=['POST'])
# def delete_book(id):
#     book = Book.query.get_or_404(id)
#     db.session.delete(book)
#     db.session.commit()
#     flash('Book deleted successfully!', 'success')
#     return redirect(url_for('index'))