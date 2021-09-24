from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    uname = StringField("What is your name?", validators=[Required()])
    submit = SubmitField('Submit')
