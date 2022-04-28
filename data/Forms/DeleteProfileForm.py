from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class DeleteProfileForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired('Введите пароль')])
    password_again = PasswordField('Password again', validators=[DataRequired()])
    submit = SubmitField('Delete profile')