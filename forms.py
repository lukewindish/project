from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from comm.models import User, Post

#Form for signing up
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #function checks to see if username submitted is already in database
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken')

    #function checks to see if email submitted is already in database
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already taken')

#Form for signing in
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
#Form for updating account
class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField('Update Info')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already taken')
#form for posting
class PostForm(FlaskForm):
    title = StringField("Item Title",validators=[DataRequired()])
    content = TextAreaField("Item Description",validators=[DataRequired()])
    price = StringField("Price")
    contact = StringField("Contact Info (Phone # or Email)")
    pic = FileField("Item Photo (Must be .jpg or .png)", validators=[FileAllowed(['jpg','png']),DataRequired()])
    submit = SubmitField('Post')
