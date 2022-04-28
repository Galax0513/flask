from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class EditPostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Theme", validators=[DataRequired()])
    files = MultipleFileField("Photo")
    submit = SubmitField('Submit')