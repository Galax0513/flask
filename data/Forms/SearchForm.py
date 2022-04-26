from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class SearchForm(FlaskForm):
    search = StringField(
        "Поиск",
        validators=[DataRequired()]
    )
    submit = SubmitField("Поиск")