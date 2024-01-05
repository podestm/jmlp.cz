import os
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import inspect
import pandas as pd
from models import Note, Event, Racer,EventHasRacer, File, Team
from config import db
import json

admin = Blueprint('admin', __name__)


@admin.route('/', methods=['GET', 'POST'])
@login_required
def home():    
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id) 
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
    return render_template('admin/home.html', user=current_user,)


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



@admin.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("admin/home.html", user=current_user)



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