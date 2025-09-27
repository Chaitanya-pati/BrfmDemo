import os
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash, jsonify, send_from_directory, make_response
from werkzeug.utils import secure_filename
from app import app, db
from models import *
from utils import allowed_file, generate_order_number, generate_job_id
import logging
import csv
import io
from sqlalchemy.sql import func

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

@app.route('/')
def index():
    """Main dashboard"""
    # Dashboard data
    pending_vehicles = Vehicle.query.filter_by(status='pending').count()
    quality_check_vehicles = Vehicle.query.filter_by(status='quality_check').count()
    try:
        pending_dispatches = Dispatch.query.filter_by(status='loaded').count()
    except:
        pending_dispatches = 0

    # Recent activities
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()

    return render_template('index.html', 
                         pending_vehicles=pending_vehicles,
                         quality_check_vehicles=quality_check_vehicles,
                         pending_dispatches=pending_dispatches,
                         recent_vehicles=recent_vehicles)

@app.route('/vehicle_entry', methods=['GET', 'POST'])
def vehicle_entry():
    if request.method == 'POST':
        try:
            # Handle file uploads
            bill_photo = None
            vehicle_photo = None

            if 'bill_photo' in request.files:
                file = request.files['bill_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bill_photo = filename

            if 'vehicle_photo' in request.files:
                file = request.files['vehicle_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"vehicle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    vehicle_photo = filename

            vehicle = Vehicle()
            vehicle.vehicle_number = request.form['vehicle_number']
            vehicle.supplier_id = int(request.form['supplier_id'])
            vehicle.driver_name = request.form.get('driver_name')
            vehicle.driver_phone = request.form.get('driver_phone')
            vehicle.bill_photo = bill_photo
            vehicle.vehicle_photo_before = vehicle_photo
            vehicle.arrival_time = datetime.now()

            db.session.add(vehicle)
            db.session.commit()
            flash('Vehicle entry recorded successfully!', 'success')
            return redirect(url_for('vehicle_entry'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error recording vehicle entry: {str(e)}', 'error')

    suppliers = Supplier.query.all()
    pending_vehicles = Vehicle.query.filter_by(status='pending').order_by(Vehicle.arrival_time.desc()).all()

    return render_template('vehicle_entry.html', suppliers=suppliers, vehicles=pending_vehicles)

@app.route('/quality_control', methods=['GET', 'POST'])
def quality_control():
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            vehicle = Vehicle.query.get_or_404(vehicle_id)

            quality_test = QualityTest()
            quality_test.vehicle_id = int(vehicle_id)
            quality_test.sample_bags_tested = int(request.form['sample_bags_tested'])
            quality_test.total_bags = int(request.form['total_bags'])
            quality_test.category_assigned = request.form['category_assigned']
            quality_test.moisture_content = float(request.form.get('moisture_content', 0))
            quality_test.quality_notes = request.form.get('quality_notes')
            quality_test.tested_by = request.form.get('lab_chemist', request.form.get('tested_by', ''))
            quality_test.approved = request.form.get('approved') == 'on'

            vehicle.status = 'quality_check'
            vehicle.quality_category = request.form['category_assigned']

            db.session.add(quality_test)
            db.session.commit()
            flash('Quality test recorded successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error recording quality test: {str(e)}', 'error')

    pending_vehicles = Vehicle.query.filter_by(status='pending').all()
    quality_tests = QualityTest.query.join(Vehicle).order_by(QualityTest.test_time.desc()).all()

    return render_template('quality_control.html', vehicles=pending_vehicles, quality_tests=quality_tests)

@app.route('/approve_vehicle/<int:vehicle_id>')
def approve_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        vehicle.owner_approved = True
        vehicle.status = 'approved'
        db.session.commit()
        flash('Vehicle approved for unloading!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving vehicle: {str(e)}', 'error')
    return redirect(url_for('quality_control'))

@app.route('/weight_entry', methods=['GET', 'POST'])
def weight_entry():
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            vehicle = Vehicle.query.get_or_404(vehicle_id)

            if 'vehicle_photo_after' in request.files:
                file = request.files['vehicle_photo_after']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"after_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    vehicle.vehicle_photo_after = filename

            vehicle.net_weight_before = float(request.form['net_weight_before'])
            vehicle.net_weight_after = float(request.form['net_weight_after'])
            vehicle.final_weight = vehicle.net_weight_before - vehicle.net_weight_after
            vehicle.godown_id = request.form['godown_id']
            vehicle.status = 'unloaded'

            # Update godown inventory
            godown = Godown.query.get(vehicle.godown_id)
            if godown:
                godown.current_stock += vehicle.final_weight

            db.session.commit()
            flash('Weight entry recorded and inventory updated!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error recording weight entry: {str(e)}', 'error')

    approved_vehicles = Vehicle.query.filter_by(status='approved', owner_approved=True).all()
    godowns = Godown.query.all()

    return render_template('weight_entry.html', vehicles=approved_vehicles, godowns=godowns)

@app.route('/precleaning', methods=['GET', 'POST'])
def precleaning():
    if request.method == 'POST':
        try:
            # Handle file uploads
            evidence_photo = None

            if 'evidence_photo' in request.files:
                file = request.files['evidence_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"precleaning_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    evidence_photo = filename

            # Check if there's already an active precleaning process
            try:
                active_process = PrecleaningProcess.query.filter_by(status='running').first()
                if active_process:
                    flash(f'Another precleaning process #{active_process.id} is already running. Please stop it first.', 'error')
                    return redirect(url_for('precleaning'))
            except:
                # If PrecleaningProcess model doesn't exist, skip the check
                pass

            # Validate stock availability
            from_godown_id = int(request.form['from_godown_id'])
            to_precleaning_bin_id = int(request.form['to_precleaning_bin_id'])
            quantity = float(request.form['quantity'])

            godown = Godown.query.get(from_godown_id)
            if not godown or godown.current_stock < quantity:
                flash('Insufficient stock in selected godown!', 'error')
                return redirect(url_for('precleaning'))

            # Create transfer record
            transfer = Transfer()
            transfer.from_godown_id = from_godown_id
            transfer.to_precleaning_bin_id = to_precleaning_bin_id
            transfer.quantity = quantity
            transfer.transfer_type = 'godown_to_precleaning'
            transfer.operator = request.form['operator']
            transfer.notes = request.form.get('notes')
            transfer.evidence_photo = evidence_photo

            # Update godown and precleaning bin stocks
            godown.current_stock -= quantity
            precleaning_bin = PrecleaningBin.query.get(to_precleaning_bin_id)
            if precleaning_bin:
                precleaning_bin.current_stock += quantity

            db.session.add(transfer)
            db.session.commit()

            flash(f'Transfer completed successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error completing transfer: {str(e)}', 'error')

    godowns = Godown.query.filter(Godown.current_stock > 0).all()
    precleaning_bins = PrecleaningBin.query.all()
    recent_transfers = Transfer.query.filter_by(transfer_type='godown_to_precleaning').order_by(Transfer.transfer_time.desc()).limit(10).all()

    return render_template('precleaning.html', 
                         godowns=godowns, 
                         precleaning_bins=precleaning_bins, 
                         transfers=recent_transfers)

@app.route('/godown_management')
def godown_management():
    godowns = Godown.query.join(GodownType).all()
    godown_types = GodownType.query.all()

    return render_template('godown_management.html', godowns=godowns, godown_types=godown_types)

@app.route('/sales_dispatch', methods=['GET', 'POST'])
def sales_dispatch():
    if request.method == 'POST':
        if request.form.get('action') == 'create_order':
            try:
                sales_order = SalesOrder()
                sales_order.order_number = generate_order_number('SO')
                sales_order.customer_id = int(request.form['customer_id'])
                sales_order.salesman = request.form.get('salesman', 'Sales Rep')
                sales_order.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
                sales_order.total_quantity = float(request.form['total_quantity'])
                sales_order.pending_quantity = float(request.form['total_quantity'])

                db.session.add(sales_order)
                db.session.commit()
                flash('Sales order created successfully!', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating sales order: {str(e)}', 'error')

        elif request.form.get('action') == 'dispatch':
            try:
                # Handle dispatch photos
                loading_photo = None
                loaded_photo = None

                if 'loading_photo' in request.files:
                    file = request.files['loading_photo']
                    if file and file.filename and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"loading_{timestamp}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loading_photo = filename

                if 'loaded_photo' in request.files:
                    file = request.files['loaded_photo']
                    if file and file.filename and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"loaded_{timestamp}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loaded_photo = filename

                # Create dispatch record
                dispatch = Dispatch()
                dispatch.dispatch_number = generate_order_number('DISP')
                dispatch.sales_order_id = int(request.form['sales_order_id'])
                dispatch.vehicle_id = int(request.form['vehicle_id'])
                dispatch.quantity = float(request.form['quantity'])
                dispatch.loading_photo = loading_photo
                dispatch.loaded_photo = loaded_photo

                # Update sales order
                sales_order = SalesOrder.query.get(dispatch.sales_order_id)
                if sales_order:
                    sales_order.delivered_quantity = (sales_order.delivered_quantity or 0) + dispatch.quantity
                    sales_order.pending_quantity = sales_order.total_quantity - sales_order.delivered_quantity

                    if sales_order.pending_quantity <= 0:
                        sales_order.status = 'completed'
                    else:
                        sales_order.status = 'partial'

                db.session.add(dispatch)
                db.session.commit()
                flash('Dispatch created successfully!', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating dispatch: {str(e)}', 'error')

    try:
        # Get data for the template with error handling
        customers = Customer.query.all() or []

        # Check if DispatchVehicle table exists, otherwise use Vehicle
        try:
            vehicles = DispatchVehicle.query.filter_by(status='available').all()
        except:
            # Fallback to Vehicle model if DispatchVehicle doesn't exist
            vehicles = Vehicle.query.filter_by(status='approved').all()

        sales_orders = SalesOrder.query.filter(SalesOrder.status.in_(['pending', 'partial'])).all() or []

        try:
            dispatches = Dispatch.query.order_by(Dispatch.dispatch_date.desc()).all()
        except:
            # If Dispatch table doesn't exist, use empty list
            dispatches = []

        return render_template('sales_dispatch.html', 
                             customers=customers, 
                             vehicles=vehicles,
                             sales_orders=sales_orders, 
                             dispatches=dispatches)

    except Exception as e:
        flash(f'Error loading sales dispatch page: {str(e)}', 'error')
        return render_template('sales_dispatch.html', 
                             customers=[], 
                             vehicles=[],
                             sales_orders=[], 
                             dispatches=[])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Configure upload folder
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])