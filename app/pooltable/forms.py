from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class PoolTableForm(FlaskForm):
    PoolTable_Name = StringField(_l('New Pool Table Pair Name'), validators=[DataRequired()])
    submit = SubmitField(_l('Save'))


class PoolTableForm_Delete(FlaskForm):
    PoolTable_Name = StringField(_l('Pool Table Pair Name'), render_kw={'readonly': True})
    confirm = BooleanField(
        'Confirmation - This action cannot be undone. Any matches previously assigned this table pairing will now show as Unassigned.')
    submit = SubmitField(_l('Delete'))
