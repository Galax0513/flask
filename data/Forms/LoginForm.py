from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Введите почту')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')