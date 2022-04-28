from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class UpdateUserForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired('Введите почту'), Email('Некорректная почта')])
    name = StringField('Name', validators=[DataRequired('Введите почту')])
    surname = StringField('Surname')
    file = FileField("Change avatar")
    submit = SubmitField('Update')