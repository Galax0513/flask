from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class RegisterForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired('Введите почту'), Email('Некорректная почта')])
    password = PasswordField('Password', validators=[DataRequired('Введите пароль')])
    password_again = PasswordField('Password again', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired('Введите почту')])
    surname = StringField('Surname')
    nickname = StringField('Nickname', validators=[DataRequired('Введите nickname'), Length(min=3, max=20,
                                                                                            message="Nickname должен быть от 4 до 20 символов")])
    age = IntegerField('Age', validators=[DataRequired('Введите возраст')])
    file = FileField("Add avatar")
    submit = SubmitField('Login')
