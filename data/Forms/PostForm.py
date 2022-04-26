from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author")
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    img = FileField("Фотографии")
    submit = SubmitField('Submit')