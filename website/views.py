import os
from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import inspect
from functions import process_upload_file
import pandas as pd
from models import Note, Event, Racer,EventHasRacer, Team
from config import db
import json

views = Blueprint('views', __name__)


@views.route('/',  methods=['GET','POST'])
def index():
    
    events = Event.query.order_by(Event.Event_date).all()
    
    cards = [{'data': event, 
              'show_button': event.Event_opened == 1,
              'event_name': event.Event_name,
              'event_date': event.Event_date,
              'event_badge': event.Event_badge,
              'event_place': event.Event_place,
              'event_closed': event.Event_opened == 0,
              'event_opened': event.Event_opened == 1,
              'propositions_file': event.Propositions_file_name,
              'results_file': event.Results_file_name
              }
        for event in events
    ]
    
    notes = Note.query.with_entities(Note.data).all()
    
    return render_template('public/index.html', user=current_user, event_list=events, notes=notes, cards=cards)


@views.route('/registration', methods=['GET','POST'])
def register():
    
    
    racers = Racer.query.with_entities(Racer.Racer_firstName, Racer.Racer_lastName, Racer.Racer_birthYear, Racer.Racer_teamName, Racer.Racer_gender).all()
    racer_list = [
    {
        'firstName': racer.Racer_firstName,
        'lastName': racer.Racer_lastName,
        'birthYear': racer.Racer_birthYear,
        'teamName': racer.Racer_teamName,
        'gender': racer.Racer_gender
    }   
        for racer in racers
    ]
    
    teams = Team.query.with_entities(Team.Team_name).all()
    
    if request.method == 'POST':
        event_name = request.form.get('event_name')
        racer_firstName = request.form.get('racer_firstName')
        racer_lastName = request.form.get('racer_lastName')
        racer_birthYear = request.form.get('racer_birthYear')
        racer_gender = request.form.get('racer_gender')
        racer_teamName = request.form.get('racer_teamName')
        racer_email = request.form.get('racer_email')
        racer_newTeam = request.form.get('racer_newTeam')
    
        existing_racer = Racer.query.filter(
            Racer.Racer_firstName == racer_firstName,
            Racer.Racer_lastName == racer_lastName,
            Racer.Racer_birthYear == racer_birthYear,
        ).with_entities(Racer.IdRacer, Racer.Racer_teamName).first()

        if existing_racer is None:
        
            if racer_teamName == 'AddNewTeam':
                racer_team = racer_newTeam
                new_team = Team(Team_name=racer_team)
                db.session.add(new_team)
                db.session.commit()
            
            new_racer = Racer(
                Racer_firstName=racer_firstName,
                Racer_lastName=racer_lastName,
                Racer_birthYear=racer_birthYear,
                Racer_teamName=racer_team,
                Racer_gender=racer_gender,
                Racer_email = racer_email
            )
            db.session.add(new_racer)
            db.session.commit()
        
        if not existing_racer[1] == racer_teamName:
            if racer_teamName == 'AddNewTeam':
                racer_team = racer_newTeam
                new_team = Team(Team_name=racer_team)
                db.session.add(new_team)
                db.session.commit()
                update_values = {'Racer_teamName': racer_team, 'Racer_email': racer_email}
            else:
                update_values = {'Racer_teamName': racer_teamName, 'Racer_email': racer_email}

            db.session.query(Racer).filter(Racer.IdRacer == existing_racer[0]).update(update_values)
            db.session.commit()

            
        matching_racer = Racer.query.filter(
            Racer.Racer_firstName == racer_firstName,
            Racer.Racer_lastName == racer_lastName,
            Racer.Racer_birthYear == racer_birthYear,
            Racer.Racer_teamName == racer_teamName
        ).first()
        matching_event = Event.query.filter(Event.Event_name == event_name).first()

        if matching_racer and matching_event:
            new_registration = EventHasRacer(EventId=matching_event.IdEvent, RacerId=matching_racer.IdRacer)
            db.session.add(new_registration)
            db.session.commit()
        
    return render_template('public/registration.html',user=current_user, racers=racers, teams=teams, racer_list=racer_list)


@views.route('/new-event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event_title = request.form.get('event_title')
        event_date = request.form.get('event_date')
        event_place = request.form.get('event_place')
        event_is_final = 1 if 'event_final' in request.form else 0
        event_badge = request.form.get('event_badge')
        event_organizator = request.form.get('event_organizator')
        event_file_propositions = request.files['event_file_propositions']
        event_file_results = request.files['event_file_results']

        existing_event = Event.query.filter(Event.IdEvent == event_id).first()
        
        if existing_event:
            prop_file_name, prop_file_ext, prop_file_url = process_upload_file(event_file_propositions, event_date, current_app.config['UPLOAD_FOLDER'])
            results_file_name, results_file_ext, results_file_url = process_upload_file(event_file_results, event_date, current_app.config['UPLOAD_FOLDER'])
                
            #event_update is an instance of the Event model
            event_update = Event(Event_name=event_title,
                                Event_date=event_date,
                                Event_place=event_place,
                                Event_final=event_is_final,
                                Results_file_name=results_file_name,
                                Results_file_ext=results_file_ext,
                                Results_file_url=results_file_url,
                                Propositions_file_name=prop_file_name,
                                Propositions_file_ext=prop_file_ext,
                                Propositions_file_url=prop_file_url,
                                Event_organizator=event_organizator,
                                Event_badge=event_badge)

            inspector = inspect(Event)
            primary_key_name = inspector.primary_key[0].name
            # Construct the update dictionary
            event_update_dict = {}
            for attribute in inspector.attrs:
                attribute_name = attribute.key
                #check for primary key and exculde it from dictioanry
                if attribute_name != primary_key_name:
                    variable_name = f"{attribute_name}"
                    # Check if the varia===ble exists and is not None
                    if hasattr(event_update, variable_name):
                        value = getattr(event_update, variable_name)
                        
                        if value is not None:
                            event_update_dict[attribute_name] = value
                            
            # Update the event with a specific IdEvent
            db.session.query(Event).filter(Event.IdEvent == event_id).update(event_update_dict)
            db.session.commit()
            
        else:   
            prop_file_name, prop_file_ext, prop_file_url = process_upload_file(event_file_propositions, event_date, current_app.config['UPLOAD_FOLDER'])
            results_file_name, results_file_ext, results_file_url = process_upload_file(event_file_results, event_date, current_app.config['UPLOAD_FOLDER'])
                
            new_event = Event(Event_name=event_title,
                                Event_date=event_date,
                                Event_place=event_place,
                                Event_final=event_is_final,
                                Propositions_file_name=prop_file_name,
                                Propositions_file_ext=prop_file_ext,
                                Propositions_file_url=prop_file_url,
                                Results_file_name=results_file_name,
                                Results_file_ext=results_file_ext,
                                Results_file_url=results_file_url,
                                Event_organizator=event_organizator,
                                Event_badge=event_badge,
                                Event_opened=0)
            
            db.session.add(new_event)
            db.session.commit()
            
    event_list = Event.query.with_entities(Event.IdEvent,Event.Event_date,Event.Event_name,Event.Event_badge, Event.Event_organizator, Event.Event_place, Event.Event_final, Event.Event_opened).order_by(Event.Event_date).all()    
    return render_template('admin/new_event.html', user=current_user, event_list=event_list)



@views.route('/open-event', methods=['GET', 'POST'])
@login_required
def open_event():
    open_event = json.loads(request.data)
    eventId = open_event['eventId']
    event = Event.query.get(eventId)
    if event is not None:
        # Toggle the Event_opened attribute (0 to 1 or 1 to 0)
        event.Event_opened = 1 if event.Event_opened == 0 else 0
        db.session.commit()
        # Return a success response
        return {'message': 'Event_opened updated successfully'}, 200
    else:
        return {'error': 'Event not found'}, 404


@views.route('/files', methods=['GET', 'POST'])
def files():

        
    return render_template('public/files.html', user=current_user)


@views.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(os.getcwd(), "uploads/" + filename)
    return send_file(file_path, as_attachment=True)


