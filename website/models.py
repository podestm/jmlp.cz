from config import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_login import UserMixin
import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
class ArchivedNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    
class File(db.Model):
    id_file =  db.Column(db.Integer, primary_key=True)
    file_upload_date = db.Column(db.Date, default=datetime.date.today)
    file_name = db.Column(db.String(255))
    file_ext = db.Column(db.String(10))
    file_url = db.Column(db.String(255))
    
class Event(db.Model):
    IdEvent = db.Column(db.Integer, primary_key=True)
    Event_name = db.Column(db.String(150))
    Event_date = db.Column(db.Date)
    Event_time = db.Column(db.Time)
    Event_place = db.Column(db.String(150))
    Event_final = db.Column(db.Integer)
    Results_file_name = db.Column(db.String(100))
    Results_file_ext = db.Column(db.String(10))
    Results_file_url = db.Column(db.String(100))
    Propositions_file_name = db.Column(db.String(100))
    Propositions_file_ext = db.Column(db.String(10))
    Propositions_file_url = db.Column(db.String(100))
    Event_organizator = db.Column(db.String(100))
    Event_badge = db.Column(db.String(100))
    Event_opened = db.Column(db.Integer)
    
class Racer(db.Model):
    IdRacer = db.Column(db.Integer, primary_key=True)
    Racer_firstName = db.Column(db.String(100))
    Racer_lastName = db.Column(db.String(100))
    Racer_birthYear = db.Column(db.String(100))
    Racer_gender = db.Column(db.Enum('Muž', 'Žena'))
    Racer_email = db.Column(db.String(100))
    Racer_teamName = db.Column(db.String(100), db.ForeignKey('team.Team_name'))
    
class EventHasRacer(db.Model):
    EventId = db.Column(db.Integer, db.ForeignKey('event.IdEvent'), primary_key=True)
    RacerId = db.Column(db.Integer, db.ForeignKey('racer.IdRacer'), primary_key=True)
    RegistrationTimestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    
class Team(db.Model):
    IdTeam = db.Column(db.Integer, primary_key=True)
    Team_name = db.Column(db.String(100))
    Team_contact = db.Column(db.String(100))
    

    
