# Create a Form Class
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email
import email_validator
from wtforms.widgets import TextArea

'''class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    nickname = StringField('Nickname',
                           validators=[DataRequired('Введите nickname'), Length(min=3, max=20,
                                                                                message="Nickname должен быть от 3 до 20 символов")])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2',
                                                                                  message='Passswords Must Match')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField('Submit')'''


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Введите почту'), Email('Некорректная почта')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired('Введите почту')])
    surname = StringField('Фамилия пользователя')
    nickname = StringField('Nickname', validators=[DataRequired('Введите nickname'), Length(min=3, max=20,
                                                                                            message="Nickname должен быть от 4 до 20 символов")])
    age = IntegerField('Возраст', validators=[DataRequired('Введите возраст')])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Введите почту')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

    # Create a Posts Form

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author")
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
    picture = FileField('Upload File', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')
    add = SubmitField('add')
