from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author")
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Theme", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    files = MultipleFileField("Photos")
    submit = SubmitField('Submit')