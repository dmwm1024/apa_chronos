from app import db
from app.models import Division, Venue
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, SelectField, PasswordField, BooleanField, SubmitField, Label
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField


class DivisionForm(FlaskForm):
    Division_Name = StringField(_l('Division Name'), validators=[DataRequired()])
    Division_Number = StringField(_l('Division Number'), validators=[DataRequired()])
    Division_Venue_ID = QuerySelectField(u'Venue', validators=[DataRequired()],
                                         query_factory=lambda: db.session.query(Venue).all(),
                                         get_pk=lambda a: a.Venue_ID, get_label=lambda a: a.Venue_Name,
                                         allow_blank=True)

    submit = SubmitField(_l('Save'))


class DivisionForm_Delete(FlaskForm):
    Division_Name = StringField(_l('Division Name'), render_kw={'readonly': True})
    confirm = BooleanField('Confirmation - This action cannot be undone. All Team, Session, and PoolTable related information will also be deleted permanently.')
    submit = SubmitField(_l('Delete'))

