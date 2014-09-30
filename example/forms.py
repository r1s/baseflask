from flask.ext.wtf import Form

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from flask.ext.babel import gettext as _


class ExampleForm(Form):
    title = StringField('title', validators=[DataRequired()])
    description = PasswordField('description', validators=[DataRequired()])
    submit = SubmitField(_('save'))