from flask import render_template, flash, redirect, url_for, request
from flask_babel import _

from app import db
from app.team import bp
from app.team.forms import TeamForm, TeamForm_Delete
from app.models import Team, Division


@bp.route('/team/<int:Division_ID>/create', methods=['GET', 'POST'])
def create(Division_ID):
    form = TeamForm()
    division = Division.query.get_or_404(Division_ID)

    if form.validate_on_submit():
        team = Team(Team_Name=form.Team_Name.data,
                    Team_Number=form.Team_Number.data,
                    Division=division.Division_ID)
        db.session.add(team)
        db.session.commit()
        flash(_('New Team has been created.'))
        return redirect(url_for('division.manage', Division_ID=division.Division_ID))

    return render_template('league/team/manage.html', title='New Team', form=form, division=division)


@bp.route('/team/<int:Team_ID>', methods=['GET', 'POST'])
def manage(Team_ID):
    team = Team.query.get_or_404(Team_ID)

    return render_template('league/team/index.html', title='Team Management', team=team)


@bp.route('/team/<int:Team_ID>/update', methods=['GET', 'POST'])
def update(Team_ID):
    form = TeamForm()
    team = Team.query.get_or_404(Team_ID)

    if request.method == 'GET':
        form.Team_Name.data = team.Team_Name
        form.Team_Number.data = team.Team_Number
        # form.Division_ID.data = team.Division.Division_ID

    if request.method == 'POST':
        team.Team_Name = form.Team_Name.data
        team.Team_Number = form.Team_Number.data
        # team.Division = form.Division_ID.data.Division_ID

        db.session.commit()
        flash(_(f'Team {team.Team_Name} has been updated.'))
        return redirect(url_for('main.index'))

    return render_template('league/team/manage.html', title=_('Manage Team'), team=team, form=form)


@bp.route('/team/<int:Team_ID>/delete', methods=['GET', 'POST'])
def delete(Team_ID):
    form = TeamForm_Delete()

    if request.method == 'GET':
        team = Team.query.get_or_404(Team_ID)
        form.Team_Name.data = team.Team_Name

    if request.method == 'POST':
        if form.confirm:
            team = Team.query.get_or_404(Team_ID)
            db.session.delete(team)
            db.session.commit()
            flash(_(f'Team {team.Team_Name} has been deleted.'))
            return redirect(url_for('main.index'))
        else:
            flash(_(f'Team {team.Team_Name} was not deleted.'))
            return redirect(url_for('main.index'))

    return render_template('league/team/manage.html', title=_('Delete Team - Confirmation'), team=team, form=form)
