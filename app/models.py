from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed passwords


class DivisionPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    division_A = db.Column(db.String(5), nullable=False)
    division_B = db.Column(db.String(5), nullable=True)
    location = db.Column(db.String(50), nullable=False)
    weeknight = db.Column(db.String(50), nullable=False)
    table_string = db.Column(db.String(50), nullable=False)


class MatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    division_ID = db.Column(db.Integer)
    match_ID = db.Column(db.Integer)
    weekOfPlay = db.Column(db.DateTime, nullable=False)
    homeTeam_ID = db.Column(db.Integer, nullable=False)
    homeTeam_Name = db.Column(db.String(50), nullable=False)
    awayTeam_ID = db.Column(db.Integer, nullable=False)
    awayTeam_Name = db.Column(db.String(50), nullable=False)
    table_number = db.Column(db.String(5), nullable=False)
