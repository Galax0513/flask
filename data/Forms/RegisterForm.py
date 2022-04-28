from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('Enter your email'), Email('Incorrect mail')])
    password = PasswordField('Password', validators=[DataRequired('Enter password'), Length(min=6, max=30)])
    password_again = PasswordField('Confirm password', validators=[DataRequired()])
    name = StringField('First name', validators=[DataRequired('Enter your name')])
    surname = StringField('Last name')
    nickname = StringField('Nickname', validators=[DataRequired('Enter your nickname'), Length(min=3, max=20,
                                                                                            message="Nickname must be between 4 and 20 characters")])
    age = IntegerField('Age', validators=[DataRequired('Enter your age')])
    file = FileField("Add photo of profile")
    submit = SubmitField('Submit')
