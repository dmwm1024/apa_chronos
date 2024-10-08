from flask import render_template, flash, redirect, url_for, request
from flask_babel import _

from app import db
from app.venue import bp
from app.venue.forms import VenueForm, VenueForm_Delete, PoolTableForm
from app.models import Venue, PoolTable, Schedule
from app.extensions import SessionLocal

from datetime import date, datetime


@bp.route('/venue', methods=['GET', 'POST'])
def index():
    db = SessionLocal()

    venues = db.query(Venue).all()

    return render_template('league/venue/index.html', title='Home', venues=venues)


@bp.route('/venue/create', methods=['GET', 'POST'])
def create():
    form = VenueForm()

    if form.validate_on_submit():
        venue = Venue(Venue_Name=form.Venue_Name.data,
                      Venue_Address=form.Venue_Address.data,
                      Venue_Phone=form.Venue_Phone.data,
                      Venue_Website=form.Venue_Website.data)
        db.session.add(venue)
        db.session.commit()
        flash(_('New Venue has been created.'))
        return redirect(url_for('main.index'))

    return render_template('league/venue/manage.html', title='New Venue', form=form)


@bp.route('/venue/<int:Venue_ID>/update', methods=['GET', 'POST'])
def update(Venue_ID):
    form = VenueForm()
    pooltable_form = PoolTableForm()

    deleteForm = VenueForm_Delete

    db = SessionLocal()
    todays_date = date.today()

    venue = db.query(Venue).filter_by(id=Venue_ID).first()

    matches_tonight_at_venue = []

    for division in venue.divisions:
        matches_tonight = db.query(Schedule).filter_by(division_id=division.id, date=todays_date).all()
        print(f'Division Name: {division.name} - Match Count: {len(matches_tonight)}')
        for match in matches_tonight:
            matches_tonight_at_venue.append(match)

    schedules = matches_tonight_at_venue

    pooltables = venue.pooltables

    if request.method == 'GET':
        form.Venue_Name.data = venue.name

    if request.method == 'POST':
        if pooltable_form.PoolTable_Name.data:
            pooltable_record = PoolTable (
                name = pooltable_form.PoolTable_Name.data,
                venue_id = Venue_ID
            )
            db.add(pooltable_record)
            db.commit()
            flash(_(f'Pool Table Pair ({pooltable_form.PoolTable_Name.data}) has been created.'))
        else:
            venue.name = form.Venue_Name.data

            db.session.commit()
            flash(_(f'Venue {venue.name} has been updated.'))
        return redirect(url_for('venue.update', Venue_ID=venue.id))

    return render_template('league/venue/manage.html', title=_('Update Venue'), pooltable_form=pooltable_form, venue=venue, schedules=schedules, pooltables=pooltables, form=form, deleteForm=deleteForm)


@bp.route('/venue/<int:Venue_ID>/delete', methods=['GET', 'POST'])
def delete(Venue_ID):
    form = VenueForm_Delete()
    db = SessionLocal()

    if request.method == 'GET':
        venue = db.query(Venue).filter_by(id=Venue_ID).first()
        form.Venue_Name.data = venue.Venue_Name

    if request.method == 'POST':
        if form.confirm:
            venue = db.query(Venue).filter_by(id=Venue_ID).first()
            db.delete(venue)
            db.commit()
            flash(_(f'Venue {venue.Venue_Name} has been deleted.'))
            return redirect(url_for('main.index'))
        else:
            flash(_(f'Venue {venue.Venue_Name} was not deleted.'))
            return redirect(url_for('main.index'))

    return render_template('league/venue/manage.html', title=_('Delete Venue'), venue=venue, form=form)