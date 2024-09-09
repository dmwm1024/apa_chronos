from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class VenueForm(FlaskForm):
    Venue_Name = StringField(_l('Venue Name'), validators=[DataRequired()])
    Venue_Address = StringField(_l('Address'))
    Venue_Phone = StringField(_l('Phone'))
    Venue_Website = StringField(_l('Website'))

    submit = SubmitField(_l('Save'))


class VenueForm_Delete(FlaskForm):
    Venue_Name = StringField(_l('Venue Name'), render_kw={'readonly': True})
    confirm = BooleanField(
        'Confirmation - This action cannot be undone. All PoolTable related information will also be deleted permanently. Any divisions assigned this Venue will now be unassigned.')
    submit = SubmitField(_l('Delete'))

