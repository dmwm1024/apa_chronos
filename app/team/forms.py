from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

from app import db
from app.models import Division


class TeamForm(FlaskForm):
    Team_Name = StringField(_l('Team Name'), validators=[DataRequired()])
    Team_Number = StringField(_l('Team Number'), validators=[DataRequired()])
    '''
    Division_ID = QuerySelectField(u'Division', validators=[DataRequired()],
                                         query_factory=lambda: db.session.query(Division).all(),
                                         get_pk=lambda a: a.Division_ID, get_label=lambda a: a.Division_Name,
                                         allow_blank=True)
    '''

    submit = SubmitField(_l('Save'))


class TeamForm_Delete(FlaskForm):
    Team_Name = StringField(_l('Team Name'), render_kw={'readonly': True})
    confirm = BooleanField(
        'Confirmation - This action cannot be undone. This will also delete all related data such as matches for this team.')
    submit = SubmitField(_l('Delete'))