from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class DivisionPairForm(FlaskForm):
    id = HiddenField("ID")
    division_a = StringField('Division A', validators=[DataRequired()])
    division_b = StringField('Division B')
    location = StringField('Location', validators=[DataRequired()])
    weeknight = SelectField('Weeknight', choices=[('', 'Please Select'), ('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ])
    table_string = StringField('Table String', validators=[DataRequired()])

    submit = SubmitField('Save')
