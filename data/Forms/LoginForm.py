from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired('Введите почту')])
    password = PasswordField('Password', validators=[DataRequired('Введите пароль')])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')