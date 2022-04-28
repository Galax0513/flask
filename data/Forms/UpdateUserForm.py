from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class UpdateUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('Enter your email'), Email('Incorrect mail')])
    name = StringField('First name', validators=[DataRequired('Enter your name')])
    surname = StringField('Last name')
    file = FileField("Change the photo of profile")
    submit = SubmitField('Update')