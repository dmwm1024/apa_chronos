from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, MultipleFileField
from wtforms.validators import DataRequired


class FileUpload(FlaskForm):
    file = MultipleFileField(_l('Select file(s) to upload:'), validators=[DataRequired()])
    submit = SubmitField(_l('Scan'))
