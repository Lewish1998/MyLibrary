from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
import sqlalchemy as sa
from app import db
from app.models import User
from flask_login import current_user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class UserSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField('Email', render_kw={'readonly': True})  # Email is now read-only
    current_password = PasswordField('Current Password', validators=[DataRequired()])  # For verifying current password
    new_password = PasswordField('New Password', validators=[Optional()])
    new_password2 = PasswordField('Repeat New Password', validators=[Optional(), EqualTo('new_password')])
    submit = SubmitField('Update Settings')

    def validate_username(self, username):
        if username.data != current_user.username:  # Ensure no duplicate username
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_current_password(self, current_password):
        if not current_user.check_password(current_password.data):  # Ensure current password matches
            raise ValidationError('Current password is incorrect.')
        
class AddBook(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    pages = StringField('Pages', validators=[Optional()])
    isbn = StringField('ISBN', validators=[Optional()])
    submit = SubmitField('Submit')

class SearchBook(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Search')
    