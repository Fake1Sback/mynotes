from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from mynotes.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[Email(),DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('User with such email address allready exists')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('User with such username allready exitsts')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[Email(),DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me',default=False)
    submit = SubmitField('Sign In')

class RequestResetForm(FlaskForm):
     email = StringField('Email',validators=[Email(),DataRequired()])
     submit = SubmitField('Request Password Reset')

     def validate_email(self,email):
         user = User.query.filter_by(email = email.data).first()
         if not user:
            raise ValidationError('There is no account with that email. Register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')