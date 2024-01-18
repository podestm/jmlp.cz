import os
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import inspect
import pandas as pd
from models import Note, Event, Racer,EventHasRacer, File, Team
from config import db
import json
from functions import process_upload_file, set_season

admin = Blueprint('admin', __name__)




@admin.route('/', methods=['GET', 'POST'])
@login_required
def home():
    posts = Note.query.all()
    blog_posts = [{'data': post,
                   'note_title': post.name,
                   'note_id': post.id,
                   'note_data': post.data,
                   'note_date': post.date,
                   'note_type': post.Note_type,
                   'note_image': post.Note_image_url != None,
                   'image_url': post.Note_image_url
                   } 
            for post in posts
    ]
        
    if request.method == 'POST': 
        note = request.form.get('note')
        title = request.form.get('post_title')
        post_date = None

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id, name=title) 
            db.session.add(new_note)
            db.session.commit()
            return redirect(url_for('admin.home'))
    return render_template('admin/home.html', user=current_user, blog_posts=blog_posts)




@admin.route('/events', methods=['GET', 'POST'])
@login_required
def events():

    event_list = Event.query.with_entities(Event.IdEvent,Event.Event_date,Event.Event_name,Event.Event_badge, Event.Event_organizator, Event.Event_place, Event.Event_final, Event.Event_opened).order_by(Event.Event_date).all()
    return render_template('admin/events.html', user=current_user, event_list=event_list)




@admin.route('/get-registrations', methods=['GET', 'POST'])
@login_required
def get_registrations():
    if request.method == "POST":
        event_id = request.form.get('event_export_id')
        
    data = db.session.query(
        Racer.Racer_firstName, 
        Racer.Racer_lastName, 
        Racer.Racer_birthYear, 
        Racer.Racer_teamName, 
        Event.Event_name
    ).join(EventHasRacer, Racer.IdRacer == EventHasRacer.RacerId
    ).join(Event, Event.IdEvent == EventHasRacer.EventId
    ).filter(EventHasRacer.EventId == event_id
    ).all()

        
    split_data = [(row.Racer_firstName, row.Racer_lastName, row.Racer_birthYear, row.Racer_teamName, row.Event_name) for row in data]
    df = pd.DataFrame(split_data, columns=["Racer_firstName", "Racer_lastName", "Racer_birthYear", "Racer_teamName", "Event_name"])

    uploads_folder_path = os.path.join(os.getcwd(), "uploads/registrations")
    os.makedirs(uploads_folder_path, exist_ok=True)  # Create the folder if it doesn't exist
    excel_file_path = os.path.join(uploads_folder_path, "registrations.xlsx")
    
    df.to_excel(excel_file_path, index=False)
    
    print(event_id)
    return send_file(excel_file_path, as_attachment=True)




@admin.route('/open-event', methods=['GET', 'POST'])
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




@admin.route('/files', methods=['GET', 'POST'])
@login_required
def file_upload():
    if request.method == "POST":
        general_file = request.files['general_file']
        file_description = request.form.get('file_description')
        
        if general_file:
                general_file_name = secure_filename(general_file.filename)
                general_file_split = general_file_ext = os.path.splitext(general_file_name)
                general_file_ext = general_file_split[1]
                general_file_url = os.path.join(current_app.config['UPLOAD_FOLDER'], general_file_name)
                general_file.save(general_file_url)
                general_file_name = general_file_split[0]

        new_file = File(file_name=general_file_name,
                        file_ext=general_file_ext,
                        file_url=general_file_url)
        
        db.session.add(new_file)
        db.session.commit()
    
    return render_template('admin/files.html', user=current_user)




@admin.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})




@admin.route('/new-event', methods=['GET', 'POST'])
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
            prop_file_name, prop_file_url = process_upload_file(event_file_propositions, event_date, current_app.config['UPLOAD_FOLDER'])
            results_file_name, results_file_url = process_upload_file(event_file_results, event_date, current_app.config['UPLOAD_FOLDER'])
            event_season = set_season(event_date)
            
            event_update = Event(Event_name=event_title,
                                Event_date=event_date,
                                Event_place=event_place,
                                Event_final=event_is_final,
                                Event_season=event_season,
                                Results_file_name=results_file_name,
                                Results_file_url=results_file_url,
                                Propositions_file_name=prop_file_name,
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
                    # Check if the variable exists and is not None
                    if hasattr(event_update, variable_name):
                        value = getattr(event_update, variable_name)
                        
                        if value is not None:
                            event_update_dict[attribute_name] = value
                            
            # Update the event with a specific IdEvent
            db.session.query(Event).filter(Event.IdEvent == event_id).update(event_update_dict)
            db.session.commit()
            
        else:   
            prop_file_name, prop_file_url = process_upload_file(event_file_propositions, event_date, current_app.config['UPLOAD_FOLDER'])
            results_file_name, results_file_url = process_upload_file(event_file_results, event_date, current_app.config['UPLOAD_FOLDER'])
            event_season = set_season(event_date)    
            
            new_event = Event(Event_name=event_title,
                                Event_date=event_date,
                                Event_place=event_place,
                                Event_final=event_is_final,
                                Event_season=event_season,
                                Propositions_file_name=prop_file_name,
                                Propositions_file_url=prop_file_url,
                                Results_file_name=results_file_name,
                                Results_file_url=results_file_url,
                                Event_organizator=event_organizator,
                                Event_badge=event_badge,
                                Event_opened=0)
            
            db.session.add(new_event)
            db.session.commit()
            
    event_list = Event.query.with_entities(Event.IdEvent,Event.Event_date,Event.Event_name,Event.Event_badge, Event.Event_organizator, Event.Event_place, Event.Event_final, Event.Event_opened).order_by(Event.Event_date).all()    
    return render_template('admin/new_event.html', user=current_user, event_list=event_list)