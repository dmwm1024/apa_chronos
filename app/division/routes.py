from flask import render_template, flash, redirect, url_for, request
from flask_babel import _

from app import db
from app.division import bp
from app.division.forms import DivisionForm, DivisionForm_Delete
from app.models import Division, Team, Match

from datetime import date, datetime


@bp.route('/division', methods=['GET', 'POST'])
def index():
    return render_template('league/division/index.html', title='Home')


@bp.route('/division/<int:Division_ID>', methods=['GET', 'POST'])
def manage(Division_ID):
    division = Division.query.get_or_404(Division_ID)
    teams = Team.query.filter_by(Division=Division_ID)

    todays_date = date.today()
    todays_date = datetime.strptime("9/13/2024", "%m/%d/%Y").date()

    matches_tonight = Match.query.filter_by(Division=division.Division_ID, Match_PlayDate=todays_date)

    return render_template('league/division/index.html', title='Division Management', division=division, teams=teams, matches_tonight=matches_tonight)



@bp.route('/division/create', methods=['GET', 'POST'])
def create():
    form = DivisionForm()

    if form.validate_on_submit():
        division = Division(Division_Name=form.Division_Name.data,
                            Division_Number=form.Division_Number.data,
                            Venue=form.Division_Venue_ID.data.Venue_ID)
        db.session.add(division)
        db.session.commit()
        flash(_('New Division has been created.'))
        return redirect(url_for('main.index'))

    return render_template('league/division/manage.html', title='New Division', form=form)


@bp.route('/division/<int:Division_ID>/update', methods=['GET', 'POST'])
def update(Division_ID):
    form = DivisionForm()
    division = Division.query.get_or_404(Division_ID)

    if request.method == 'GET':
        form.Division_Name.data = division.Division_Name
        form.Division_Number.data = division.Division_Number
        form.Division_Venue_ID.data = division.Venue_rel

    if request.method == 'POST':
        division.Division_Name = form.Division_Name.data
        division.Division_Number = form.Division_Number.data
        division.Venue = form.Division_Venue_ID.data.Venue_ID

        db.session.commit()
        flash(_(f'Division {division.Division_Name} has been updated.'))
        return redirect(url_for('main.index'))

    return render_template('league/division/manage.html', title=_('Manage Division'), division=division, form=form)

@bp.route('/division/<int:Division_ID>/delete', methods=['GET', 'POST'])
def delete(Division_ID):
    form = DivisionForm_Delete()
    division = Division.query.get_or_404(Division_ID)

    if request.method == 'GET':
        form.Division_Name.data = division.Division_Name

    if request.method == 'POST':
        if form.confirm:
            db.session.delete(division)
            db.session.commit()
            flash(_(f'Division {division.Division_Name} has been deleted.'))
            return redirect(url_for('main.index'))
        else:
            flash(_(f'Division {division.Division_Name} was not deleted.'))
            return redirect(url_for('main.index'))

    return render_template('league/division/manage.html', title=_('Delete Division'), division=division, form=form)
