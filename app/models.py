from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)

    # Relationships
    divisions = relationship('Division', back_populates='session')


class Division(Base):
    __tablename__ = "divisions"
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    number = Column(String, nullable=False)
    format = Column(String, nullable=False)
    type = Column(String, nullable=False)
    night_of_play = Column(String, nullable=False)
    is_mine = Column(Boolean, default=False)

    # Foreign key to the Session table
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)

    # One-to-one ForeignKey to the Venue table - Not Found?
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=True)

    # Relationships with Session, Teams, and Schedules
    session = relationship('Session', back_populates='divisions')
    teams = relationship('Team', back_populates='division')
    schedules = relationship('Schedule', back_populates='division')

    # Relationship with Venue (one-to-one)
    venue = relationship('Venue', back_populates='division', uselist=False)


class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=False)  # Assuming team ID is externally provided
    name = Column(String, nullable=False)
    number = Column(String, nullable=False)

    # ForeignKey linking to Division and Venue
    division_id = Column(Integer, ForeignKey('divisions.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=True)

    # Relationships with Division and Venue
    division = relationship('Division', back_populates='teams')
    venue = relationship('Venue', back_populates='teams')

    # Relationships for matches
    home_matches = relationship('Schedule', foreign_keys='Schedule.home_team_id', back_populates='home_team')
    away_matches = relationship('Schedule', foreign_keys='Schedule.away_team_id', back_populates='away_team')

    # Combined relationship to easily access all matches where the team is involved
    @property
    def all_matches(self):
        return sorted(self.home_matches + self.away_matches, key=lambda match: match.date)


class Venue(Base):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True, autoincrement=False)  # Assuming venue ID is externally provided
    name = Column(String, nullable=False)

    # One-to-one relationship with Division
    division = relationship('Division', back_populates='venue', uselist=False)

    # Relationships with Teams, PoolTables and Schedules
    teams = relationship('Team', back_populates='venue')
    schedules = relationship('Schedule', back_populates='venue')
    pooltables = relationship('PoolTable', back_populates='venue')


class PoolTable(Base):
    __tablename__ = "pooltables"
    id = Column(Integer, primary_key=True, autoincrement=True)  # Assuming venue ID is externally provided
    name = Column(String, nullable=False)

    # ForeignKey linking PoolTable to Venue
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)

    # Relationship with Venue
    venue = relationship('Venue', back_populates='pooltables')

    # Relationship with Schedule
    schedules = relationship('Schedule', back_populates='pooltable')


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True, autoincrement=False)  # Assuming schedule ID is externally provided
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    week_of_play = Column(Integer, nullable=True)
    skip = Column(Boolean, default=False)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)

    # ForeignKey linking to PoolTable
    pooltable_id = Column(Integer, ForeignKey('pooltables.id'), nullable=True)

    # ForeignKey linking to Division and Venue
    division_id = Column(Integer, ForeignKey('divisions.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=True)

    # Relationships with Division and Venue
    division = relationship('Division', back_populates='schedules')
    venue = relationship('Venue', back_populates='schedules')
    pooltable = relationship('PoolTable', back_populates='schedules')

    # Relationships for home and away teams
    home_team = relationship('Team', foreign_keys=[home_team_id])
    away_team = relationship('Team', foreign_keys=[away_team_id])
