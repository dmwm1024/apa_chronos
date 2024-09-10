from flask import render_template, flash, redirect, url_for, request
from flask_babel import _

from app import db
from app.pooltable import bp
from app.pooltable.forms import PoolTableForm, PoolTableForm_Delete
from app.models import PoolTable, Team, Division, Venue

from app.extensions import SessionLocal

@bp.route('/pooltable/<int:Venue_ID>/create', methods=['GET', 'POST'])
def create(Venue_ID):
    db = SessionLocal()

    form = PoolTableForm()

    venue = db.query(Venue).filter_by(id=Venue_ID).first()

    if form.validate_on_submit():
        pooltable_record =  PoolTable(
            name=form.PoolTable_Name.data,
            venue_id=venue.id
        )
        db.add(pooltable_record)
        db.commit()
        flash(_('New Pool Table Pair has been created.'))
        return redirect(url_for('venue.update', Venue_ID=venue.id))

    return render_template('league/venue/manage.html', title='New Pool Table Pair', form=form, venue=venue)


@bp.route('/pooltable/<int:PoolTable_ID>', methods=['GET', 'POST'])
def manage(PoolTable_ID):
    pooltable = PoolTable.query.get_or_404(PoolTable_ID)

    return render_template('league/pooltable/index.html', title='Pool Table Pair Management', pooltable=pooltable)


@bp.route('/pooltable/<int:PoolTable_ID>/update', methods=['GET', 'POST'])
def update(PoolTable_ID):
    form = PoolTableForm()

    if request.method == 'GET':
        pooltable = PoolTable.query.get_or_404(PoolTable_ID)
        form.PoolTable_Name.data = pooltable.PoolTable_Name

    if request.method == 'POST':
        pooltable = PoolTable.query.get_or_404(PoolTable_ID)
        pooltable.PoolTable_Name = form.PoolTable_Name.data

        db.session.commit()
        flash(_(f'Pool Table Pair {pooltable.PoolTable_Name} has been updated.'))
        return redirect(url_for('main.index'))

    return render_template('league/pooltable/manage.html', title=_('Manage Pool Table Pair'), pooltable=pooltable, form=form)


@bp.route('/pooltable/<int:PoolTable_ID>/delete', methods=['GET', 'POST'])
def delete(PoolTable_ID):
    form = PoolTableForm_Delete()
    db = SessionLocal()

    if request.method == 'GET':
        pooltable = db.query(PoolTable).filter_by(id=PoolTable_ID).first()
        form.PoolTable_Name.data = pooltable.name

    if request.method == 'POST':
        if form.confirm:
            pooltable = db.query(PoolTable).filter_by(id=PoolTable_ID).first()

            db.delete(pooltable)
            db.commit()
            flash(_(f'Table {pooltable.name} has been deleted.'))
            return redirect(url_for('venue.update', Venue_ID=pooltable.venue_id))
        else:
            flash(_(f'Table {pooltable.name} was not deleted.'))
            return redirect(url_for('venue.update', Venue_ID=pooltable.venue_id))

    return render_template('league/pooltable/manage.html', title=_('Delete Team - Confirmation'), pooltable=pooltable, form=form)

