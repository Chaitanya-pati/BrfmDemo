import os
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import *

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

@app.route('/init_cleaning_reminders')
def init_cleaning_reminders():
    """Initialize sample cleaning reminders for existing machines"""
    try:
        machines = ProductionMachine.query.all()

        for machine in machines:
            # Check if reminder already exists
            existing = MachineCleaningReminder.query.filter_by(
                machine_id=machine.id, 
                is_active=True
            ).first()

            if not existing:
                # Create default reminder based on machine type
                frequency_hours = 3  # Default 3 hours
                if machine.machine_type == 'packer':
                    frequency_hours = 4  # Packing machines every 4 hours

                reminder = MachineCleaningReminder(
                    machine_id=machine.id,
                    frequency_hours=frequency_hours,
                    next_cleaning_due=datetime.utcnow() + timedelta(hours=frequency_hours),
                    is_active=True
                )
                db.session.add(reminder)

        db.session.commit()
        flash('Cleaning reminders initialized successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error initializing cleaning reminders: {str(e)}', 'error')

    return redirect(url_for('configure_cleaning_frequencies'))