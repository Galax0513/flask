# Create a Form Class
from flask_wtf import FlaskForm
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



    # Create a Posts Form



