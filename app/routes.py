from app import app, db
from app.models import User, Book
from app.forms import UserForm, BookForm, RegistrationForm, LoginForm
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as sa


@app.route('/')
@login_required
def index():
    # users = User.query.all()
    # books = Book.query.all()
    # return render_template('index.html', users=users, books=books)
    return 'success'

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





# CRUD Operations for Users
@app.route('/user/new', methods=['GET', 'POST'])
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(name=form.name.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('user_form.html', form=form)

@app.route('/user/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('user_form.html', form=form)

@app.route('/user/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('index'))

# CRUD Operations for Books
@app.route('/book/new', methods=['GET', 'POST'])
def new_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, author=form.author.data, user_id=form.user_id.data)
        db.session.add(book)
        db.session.commit()
        flash('Book created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('book_form.html', form=form)

@app.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.user_id = form.user_id.data
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('book_form.html', form=form)

@app.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('index'))