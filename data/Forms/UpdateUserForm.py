from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email


class UpdateUserForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('Enter email'), Email('Incorrect email')])
    name = StringField('First name', validators=[DataRequired('Enter name')])
    surname = StringField('Last name')
    nickname = StringField('Nickname', validators=[DataRequired('Enter nickname'), Length(min=3, max=20,
                                                                                            message="Nickname must be between 4 and 20 characters")])
    file = FileField("Change photo of profile")
    submit = SubmitField('Submit')