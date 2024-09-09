from flask import render_template, flash, redirect, url_for, request
from flask_babel import _

from app import db
from app.venue import bp
from app.venue.forms import VenueForm, VenueForm_Delete
from app.models import Venue, PoolTable


@bp.route('/venue', methods=['GET', 'POST'])
def index():
    venues = Venue.query.all()
    print('Test - Venue.Routes')
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
    deleteForm = VenueForm_Delete
    venue = Venue.query.get_or_404(Venue_ID)
    pooltables = PoolTable.query.filter_by(Venue=Venue_ID)

    if request.method == 'GET':
        form.Venue_Name.data = venue.Venue_Name
        form.Venue_Address.data = venue.Venue_Address
        form.Venue_Phone.data = venue.Venue_Phone
        form.Venue_Website.data = venue.Venue_Website

    if request.method == 'POST':
        venue.Venue_Name = form.Venue_Name.data
        venue.Venue_Address = form.Venue_Address.data
        venue.Venue_Phone = form.Venue_Phone.data
        venue.Venue_Website = form.Venue_Website.data

        db.session.commit()
        flash(_(f'Venue {venue.Venue_Name} has been updated.'))
        return redirect(url_for('venue.index'))

    return render_template('league/venue/manage.html', title=_('Update Venue'), venue=venue, pooltables=pooltables, form=form, deleteForm=deleteForm)


@bp.route('/venue/<int:Venue_ID>/delete', methods=['GET', 'POST'])
def delete(Venue_ID):
    form = VenueForm_Delete()

    if request.method == 'GET':
        venue = Venue.query.get_or_404(Venue_ID)
        form.Venue_Name.data = venue.Venue_Name

    if request.method == 'POST':
        if form.confirm:
            venue = Venue.query.get_or_404(Venue_ID)
            db.session.delete(venue)
            db.session.commit()
            flash(_(f'Venue {venue.Venue_Name} has been deleted.'))
            return redirect(url_for('main.index'))
        else:
            flash(_(f'Venue {venue.Venue_Name} was not deleted.'))
            return redirect(url_for('main.index'))

    return render_template('league/venue/manage.html', title=_('Delete Venue'), venue=venue, form=form)