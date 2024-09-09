import datetime
from typing import List

from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .extensions import db


class Division(db.Model):
    __tablename__ = "Division"
    Division_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Division_Number: Mapped[str] = mapped_column(String())
    Division_Name: Mapped[str] = mapped_column(String())

    # One to Many Relationships
    teams: Mapped[List["Team"]] = relationship(cascade="all,delete")
    matches: Mapped[List["Match"]] = relationship(cascade="all,delete")

    # One to One Relationships
    Venue: Mapped[int] = mapped_column(ForeignKey("Venue.Venue_ID"))
    Venue_rel = relationship("Venue", foreign_keys="Division.Venue")


class Venue(db.Model):
    __tablename__ = "Venue"
    Venue_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Venue_Name: Mapped[str] = mapped_column(String())
    Venue_Address: Mapped[str] = mapped_column(String(), nullable=True)
    Venue_Phone: Mapped[str] = mapped_column(String(), nullable=True)
    Venue_Website: Mapped[str] = mapped_column(String(), nullable=True)

    # One to Many Relationships
    pooltables: Mapped[List["PoolTable"]] = relationship(cascade="all,delete")


class PoolTable(db.Model):
    __tablename__ = "PoolTable"
    PoolTable_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    PoolTable_Name: Mapped[str] = mapped_column(String())
    Venue: Mapped[int] = mapped_column(ForeignKey("Venue.Venue_ID"))


class TableAvailability(db.Model):
    __tablename__ = "TableAvailability"
    TableAvailability_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Division: Mapped[int] = mapped_column(ForeignKey("Division.Division_ID"))
    Venue: Mapped[int] = mapped_column(ForeignKey("Venue.Venue_ID"))
    PoolTable: Mapped[int] = mapped_column(ForeignKey("PoolTable.PoolTable_ID"))


class Team(db.Model):
    __tablename__ = "Team"
    Team_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Team_Number: Mapped[str] = mapped_column(String())
    Team_Name: Mapped[str] = mapped_column(String())
    Division: Mapped[int] = mapped_column(ForeignKey("Division.Division_ID"))

    # Relationships for matches where the team is the home team
    home_matches: Mapped[List["Match"]] = relationship("Match", foreign_keys="[Match.HomeTeam]", back_populates="home_team", cascade="all,delete")

    # Relationships for matches where the team is the away team
    away_matches: Mapped[List["Match"]] = relationship("Match", foreign_keys="[Match.AwayTeam]", back_populates="away_team", cascade="all,delete")

    # Hybrid property to combine both home and away matches
    @hybrid_property
    def all_matches(self):
        return self.home_matches + self.away_matches

    # Alternatively, you can use a method if you prefer:
    def get_all_matches(self):
        return self.home_matches + self.away_matches


class Match(db.Model):
    __tablename__ = "Match"
    Match_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    Match_WeekNum: Mapped[str] = mapped_column(String())
    Match_PlayDate: Mapped[datetime.date] = mapped_column(Date())
    Division: Mapped[int] = mapped_column(ForeignKey("Division.Division_ID"))
    HomeTeam: Mapped[int] = mapped_column(ForeignKey("Team.Team_ID"))
    AwayTeam: Mapped[int] = mapped_column(ForeignKey("Team.Team_ID"))
    Venue: Mapped[int] = mapped_column(ForeignKey("Venue.Venue_ID"))
    PoolTable: Mapped[int] = mapped_column(ForeignKey("PoolTable.PoolTable_ID"))
    PoolTable_rel = relationship("PoolTable", foreign_keys="Match.PoolTable")

    # One-to-many relationship for the home team
    home_team = relationship("Team", foreign_keys=[HomeTeam], back_populates="home_matches")

    # One-to-many relationship for the away team
    away_team = relationship("Team", foreign_keys=[AwayTeam], back_populates="away_matches")