from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class DeleteProfileForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Удалить профиль')