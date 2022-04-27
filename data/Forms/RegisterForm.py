from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Введите почту'), Email('Некорректная почта')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired('Введите почту')])
    surname = StringField('Фамилия пользователя')
    nickname = StringField('Nickname', validators=[DataRequired('Введите nickname'), Length(min=3, max=20,
                                                                                            message="Nickname должен быть от 4 до 20 символов")])
    age = IntegerField('Возраст', validators=[DataRequired('Введите возраст')])
    file = FileField("Добавить аватар")
    submit = SubmitField('Войти')
