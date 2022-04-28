from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class UpdateUserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Введите почту'), Email('Некорректная почта')])
    name = StringField('Имя пользователя', validators=[DataRequired('Введите почту')])
    surname = StringField('Фамилия пользователя')
    file = FileField("Изменить аватар")
    submit = SubmitField('Обновить')