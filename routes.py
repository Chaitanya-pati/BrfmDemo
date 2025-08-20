import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from app import app, db
from models import (Vehicle, Supplier, Godown, GodownType, QualityTest, Transfer, 
                   PrecleaningBin, ProductionOrder, ProductionPlan, ProductionPlanItem, ProductionJobNew,
                   Customer, Product, SalesDispatch, CleaningProcess, CleaningMachine,
                   ProductionTransfer, GrindingProcess, ProductOutput, PackingProcess,
                   CleaningLog, StorageArea, StorageTransfer)
from utils import allowed_file, generate_order_number, generate_job_id

@app.route('/')
def index():
    # Dashboard statistics
    total_vehicles = Vehicle.query.count()
    pending_vehicles = Vehicle.query.filter_by(status='pending').count()
    approved_vehicles = Vehicle.query.filter_by(status='approved').count()
    
    total_stock = db.session.query(db.func.sum(Godown.current_stock)).scalar() or 0
    active_orders = ProductionOrder.query.filter_by(status='pending').count()
    
    recent_vehicles = Vehicle.query.order_by(Vehicle.entry_time.desc()).limit(5).all()
    recent_quality_tests = QualityTest.query.join(Vehicle).order_by(QualityTest.test_time.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_vehicles=total_vehicles,
                         pending_vehicles=pending_vehicles,
                         approved_vehicles=approved_vehicles,
                         quality_check_vehicles=pending_vehicles,  # Add this for template
                         total_stock=total_stock,
                         active_orders=active_orders,
                         recent_vehicles=recent_vehicles,
                         recent_quality_tests=recent_quality_tests)

@app.route('/vehicle_entry', methods=['GET', 'POST'])
def vehicle_entry():
    if request.method == 'POST':
        try:
            # Handle file uploads
            vehicle_photo = None
            supplier_bill = None
            
            if 'vehicle_photo' in request.files:
                file = request.files['vehicle_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"vehicle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    vehicle_photo = filename
            
            if 'supplier_bill' in request.files:
                file = request.files['supplier_bill']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    supplier_bill = filename
            
            # Create vehicle record
            vehicle = Vehicle()
            vehicle.supplier_id = int(request.form['supplier_id'])
            vehicle.vehicle_number = request.form['vehicle_number']
            vehicle.driver_name = request.form['driver_name']
            vehicle.driver_phone = request.form.get('driver_phone')
            vehicle.arrival_time = datetime.strptime(request.form['arrival_time'], '%Y-%m-%dT%H:%M')
            vehicle.entry_time = vehicle.arrival_time  # Add entry_time field
            vehicle.vehicle_photo = vehicle_photo
            vehicle.supplier_bill = supplier_bill
            vehicle.notes = request.form.get('notes')
            vehicle.status = 'pending'
            
            db.session.add(vehicle)
            db.session.commit()
            flash('Vehicle entry recorded successfully!', 'success')
            return redirect(url_for('vehicle_entry'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording vehicle entry: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    recent_vehicles = Vehicle.query.order_by(Vehicle.entry_time.desc()).limit(10).all()
    
    return render_template('vehicle_entry.html', suppliers=suppliers, recent_vehicles=recent_vehicles)

@app.route('/quality_control', methods=['GET', 'POST'])
def quality_control():
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            vehicle = Vehicle.query.get_or_404(vehicle_id)
            
            # Handle file uploads for sample photos
            sample_photos_before = None
            sample_photos_after = None
            
            if 'sample_photos_before' in request.files:
                file = request.files['sample_photos_before']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"sample_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    sample_photos_before = filename
            
            if 'sample_photos_after' in request.files:
                file = request.files['sample_photos_after']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"sample_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    sample_photos_after = filename
            
            # Create quality test record
            quality_test = QualityTest()
            quality_test.vehicle_id = int(vehicle_id)
            quality_test.sample_bags_tested = int(request.form['sample_bags_tested'])
            quality_test.total_bags = int(request.form['total_bags'])
            quality_test.category_assigned = request.form['category_assigned']
            quality_test.moisture_content = float(request.form.get('moisture_content', 0)) if request.form.get('moisture_content') else None
            quality_test.foreign_matter = float(request.form.get('foreign_matter', 0)) if request.form.get('foreign_matter') else None
            quality_test.broken_grains = float(request.form.get('broken_grains', 0)) if request.form.get('broken_grains') else None
            quality_test.shrivelled_broken = float(request.form.get('shrivelled_broken', 0)) if request.form.get('shrivelled_broken') else None
            quality_test.damaged = float(request.form.get('damaged', 0)) if request.form.get('damaged') else None
            quality_test.weevilled = float(request.form.get('weevilled', 0)) if request.form.get('weevilled') else None
            quality_test.other_food_grains = float(request.form.get('other_food_grains', 0)) if request.form.get('other_food_grains') else None
            quality_test.sprouted = float(request.form.get('sprouted', 0)) if request.form.get('sprouted') else None
            quality_test.immature = float(request.form.get('immature', 0)) if request.form.get('immature') else None
            quality_test.test_weight = float(request.form.get('test_weight', 0)) if request.form.get('test_weight') else None
            quality_test.gluten = float(request.form.get('gluten', 0)) if request.form.get('gluten') else None
            quality_test.protein = float(request.form.get('protein', 0)) if request.form.get('protein') else None
            quality_test.falling_number = float(request.form.get('falling_number', 0)) if request.form.get('falling_number') else None
            quality_test.ash_content = float(request.form.get('ash_content', 0)) if request.form.get('ash_content') else None
            quality_test.wet_gluten = float(request.form.get('wet_gluten', 0)) if request.form.get('wet_gluten') else None
            quality_test.dry_gluten = float(request.form.get('dry_gluten', 0)) if request.form.get('dry_gluten') else None
            quality_test.sedimentation_value = float(request.form.get('sedimentation_value', 0)) if request.form.get('sedimentation_value') else None
            quality_test.quality_notes = request.form.get('quality_notes')
            quality_test.lab_instructor = request.form['lab_instructor']
            quality_test.approved = request.form.get('approved') == 'on'
            quality_test.sample_photos_before = sample_photos_before
            quality_test.sample_photos_after = sample_photos_after
            
            # Set test date if provided, otherwise use current time
            if request.form.get('test_date'):
                quality_test.test_time = datetime.strptime(request.form['test_date'], '%Y-%m-%dT%H:%M')
            
            # Update vehicle with quality info
            vehicle.quality_category = request.form['category_assigned']
            vehicle.status = 'quality_check'
            
            if quality_test.approved:
                vehicle.owner_approved = True
                vehicle.status = 'approved'
            
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

@app.route('/reject_vehicle/<int:vehicle_id>')
def reject_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        vehicle.status = 'rejected'
        db.session.commit()
        flash('Vehicle rejected!', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting vehicle: {str(e)}', 'error')
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

@app.route('/godown_management')
def godown_management():
    godowns = Godown.query.join(GodownType).all()
    godown_types = GodownType.query.all()
    
    return render_template('godown_management.html', godowns=godowns, godown_types=godown_types)

@app.route('/precleaning', methods=['GET', 'POST'])
def precleaning():
    if request.method == 'POST':
        try:
            # Handle transfer photos
            transfer_photo = None
            
            if 'transfer_photo' in request.files:
                file = request.files['transfer_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    transfer_photo = filename
            
            transfer = Transfer()
            transfer.from_godown_id = int(request.form['from_godown_id'])
            transfer.to_precleaning_bin_id = int(request.form['to_precleaning_bin_id'])
            transfer.quantity = float(request.form['quantity'])
            transfer.transfer_type = 'godown_to_precleaning'
            transfer.operator = request.form['operator']
            transfer.notes = request.form.get('notes')
            transfer.evidence_photo = transfer_photo
            
            # Update stocks
            from_godown = Godown.query.get(transfer.from_godown_id)
            to_bin = PrecleaningBin.query.get(transfer.to_precleaning_bin_id)
            
            if from_godown and to_bin:
                from_godown.current_stock -= transfer.quantity
                to_bin.current_stock += transfer.quantity
            
            db.session.add(transfer)
            db.session.commit()
            flash('Transfer completed successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing transfer: {str(e)}', 'error')
    
    godowns = Godown.query.filter(Godown.current_stock > 0).all()
    precleaning_bins = PrecleaningBin.query.all()
    recent_transfers = Transfer.query.filter_by(transfer_type='godown_to_precleaning').order_by(Transfer.transfer_time.desc()).limit(10).all()
    
    return render_template('precleaning.html', godowns=godowns, precleaning_bins=precleaning_bins, transfers=recent_transfers)

@app.route('/production_orders', methods=['GET', 'POST'])
def production_orders():
    if request.method == 'POST':
        try:
            production_order = ProductionOrder()
            production_order.order_number = generate_order_number('PO')
            production_order.quantity = float(request.form['quantity'])
            production_order.product = request.form['product']
            production_order.customer_id = int(request.form['customer_id']) if request.form.get('customer_id') else None
            production_order.customer = request.form.get('customer')  # Keep the string field too
            production_order.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
            production_order.priority = request.form.get('priority', 'normal')
            production_order.description = request.form.get('notes')
            production_order.created_by = request.form.get('created_by', 'System')
            
            db.session.add(production_order)
            db.session.commit()
            flash('Production order created successfully!', 'success')
            return redirect(url_for('production_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production order: {str(e)}', 'error')
    
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    customers = Customer.query.all()
    products = Product.query.filter_by(category='Main Product').all()
    
    return render_template('production_orders.html', orders=orders, customers=customers, products=products)

@app.route('/production_execution', methods=['GET', 'POST'])
def production_execution():
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'start_job':
                plan = ProductionPlan.query.get(int(request.form['plan_id']))
                if not plan:
                    flash('Production plan not found!', 'error')
                    return redirect(url_for('production_execution'))
                
                # Create initial transfer job
                job = ProductionJobNew()
                job.order_id = plan.order_id
                job.plan_id = plan.id
                job.job_number = generate_job_id()
                job.stage = 'transfer'
                job.status = 'pending'
                job.started_by = request.form['started_by']
                job.notes = request.form.get('notes')
                
                db.session.add(job)
                db.session.commit()
                flash('Production job created successfully! Start with the transfer stage.', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing request: {str(e)}', 'error')
    
    # Get pipeline statistics
    pipeline_stats = {
        'transfer': ProductionJobNew.query.filter_by(stage='transfer', status='in_progress').count(),
        'cleaning_24h': ProductionJobNew.query.filter_by(stage='cleaning_24h', status='in_progress').count(),
        'cleaning_12h': ProductionJobNew.query.filter_by(stage='cleaning_12h', status='in_progress').count(),
        'grinding': ProductionJobNew.query.filter_by(stage='grinding', status='in_progress').count(),
        'packing': ProductionJobNew.query.filter_by(stage='packing', status='in_progress').count(),
        'completed': ProductionJobNew.query.filter_by(status='completed').count()
    }
    
    # Get active jobs with enhanced data
    active_jobs = ProductionJobNew.query.filter(
        ProductionJobNew.status.in_(['pending', 'in_progress'])
    ).order_by(ProductionJobNew.created_at.desc()).all()
    
    # Enhance jobs with additional data
    for job in active_jobs:
        job.stage_display = job.stage.replace('_', ' ').title()
        job.status_color = {
            'pending': 'secondary',
            'in_progress': 'primary', 
            'completed': 'success',
            'paused': 'warning'
        }.get(job.status, 'secondary')
        
        # Get end time for cleaning processes
        if job.stage in ['cleaning_24h', 'cleaning_12h'] and job.status == 'in_progress':
            cleaning_process = CleaningProcess.query.filter_by(job_id=job.id, status='running').first()
            if cleaning_process:
                job.end_time = cleaning_process.end_time
    
    # Get approved plans for starting new jobs
    approved_plans = ProductionPlan.query.filter_by(status='approved').join(ProductionOrder).all()
    
    # Get machine cleaning status
    machines = CleaningMachine.query.all()
    for machine in machines:
        if machine.last_cleaned:
            time_since_cleaned = datetime.utcnow() - machine.last_cleaned
            hours_since_cleaned = time_since_cleaned.total_seconds() / 3600
            
            if hours_since_cleaned < machine.cleaning_frequency_hours:
                machine.status_class = 'status-clean'
                machine.needs_cleaning = False
                remaining_hours = machine.cleaning_frequency_hours - hours_since_cleaned
                machine.next_cleaning_in = f"{int(remaining_hours)}h {int((remaining_hours % 1) * 60)}m"
            elif hours_since_cleaned < machine.cleaning_frequency_hours * 1.2:
                machine.status_class = 'status-needs-cleaning'
                machine.needs_cleaning = True
                machine.next_cleaning_in = "Due now"
            else:
                machine.status_class = 'status-overdue'
                machine.needs_cleaning = True
                machine.next_cleaning_in = "Overdue"
                
            machine.last_cleaned_ago = f"{int(hours_since_cleaned)}h ago"
        else:
            machine.status_class = 'status-overdue'
            machine.needs_cleaning = True
            machine.last_cleaned_ago = "Never"
            machine.next_cleaning_in = "Overdue"
    
    return render_template('production_execution_new.html',
                         active_jobs=active_jobs,
                         approved_plans=approved_plans,
                         pipeline_stats=pipeline_stats,
                         machines=machines)

# API Routes for production execution
@app.route('/production_execution/start_job/<int:job_id>', methods=['POST'])
def start_production_job(job_id):
    try:
        job = ProductionJobNew.query.get_or_404(job_id)
        
        if job.status != 'pending':
            return jsonify({'success': False, 'message': 'Job is not in pending state'})
        
        job.status = 'in_progress'
        job.started_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Job started successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/production_execution/complete_job/<int:job_id>')
def complete_production_job(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if job.stage == 'transfer':
        return redirect(url_for('transfer_execution', job_id=job_id))
    elif job.stage == 'cleaning_24h':
        return redirect(url_for('cleaning_24h_execution', job_id=job_id))
    elif job.stage == 'cleaning_12h':
        return redirect(url_for('cleaning_12h_execution', job_id=job_id))
    elif job.stage == 'grinding':
        return redirect(url_for('grinding_execution', job_id=job_id))
    elif job.stage == 'packing':
        return redirect(url_for('packing_execution', job_id=job_id))
    
    return redirect(url_for('production_execution'))

# Transfer Execution
@app.route('/production_execution/transfer/<int:job_id>', methods=['GET', 'POST'])
def transfer_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            # Create transfer record
            transfer = ProductionTransfer()
            transfer.job_id = job_id
            transfer.from_precleaning_bin_id = int(request.form['from_bin_id'])
            transfer.quantity_transferred = float(request.form['quantity'])
            transfer.operator_name = request.form['operator_name']
            
            # Handle file uploads
            if 'start_photo' in request.files:
                file = request.files['start_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"transfer_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    transfer.start_photo = filename
            
            if 'end_photo' in request.files:
                file = request.files['end_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"transfer_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    transfer.end_photo = filename
            
            db.session.add(transfer)
            
            # Update precleaning bin stock
            from_bin = PrecleaningBin.query.get(transfer.from_precleaning_bin_id)
            from_bin.current_stock -= transfer.quantity_transferred
            
            # Complete current job and create next job
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = transfer.operator_name
            
            # Create 24h cleaning job
            cleaning_job = ProductionJobNew()
            cleaning_job.order_id = job.order_id
            cleaning_job.plan_id = job.plan_id
            cleaning_job.job_number = generate_job_id()
            cleaning_job.stage = 'cleaning_24h'
            cleaning_job.status = 'pending'
            
            db.session.add(cleaning_job)
            db.session.commit()
            
            flash('Transfer completed successfully! 24-hour cleaning job created.', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing transfer: {str(e)}', 'error')
    
    plan_items = ProductionPlanItem.query.filter_by(plan_id=job.plan_id).all()
    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    
    return render_template('transfer_execution.html', 
                         job=job, 
                         plan_items=plan_items,
                         precleaning_bins=precleaning_bins)

# 24 Hour Cleaning Process
@app.route('/production_execution/cleaning_24h/<int:job_id>', methods=['GET', 'POST'])
def cleaning_24h_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            # Create cleaning process record
            cleaning = CleaningProcess()
            cleaning.job_id = job_id
            cleaning.process_type = '24_hour'
            cleaning.duration_hours = int(request.form.get('duration_hours', 24))
            cleaning.start_time = datetime.utcnow()
            cleaning.end_time = datetime.utcnow() + timedelta(hours=cleaning.duration_hours)
            cleaning.start_moisture = float(request.form['start_moisture'])
            cleaning.water_added_liters = float(request.form.get('water_added', 0))
            cleaning.operator_name = request.form['operator_name']
            cleaning.status = 'running'
            
            # Handle file uploads
            if 'start_photo' in request.files:
                file = request.files['start_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"cleaning24h_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cleaning.start_photo = filename
            
            db.session.add(cleaning)
            
            # Update job status
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'{cleaning.duration_hours}-hour cleaning process started successfully!', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting cleaning process: {str(e)}', 'error')
    
    return render_template('cleaning_24h_execution.html', job=job)

# 12 Hour Cleaning Process  
@app.route('/production_execution/cleaning_12h/<int:job_id>', methods=['GET', 'POST'])
def cleaning_12h_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            # Create cleaning process record
            cleaning = CleaningProcess()
            cleaning.job_id = job_id
            cleaning.process_type = '12_hour'
            cleaning.duration_hours = int(request.form.get('duration_hours', 12))
            cleaning.target_moisture = float(request.form['target_moisture'])
            cleaning.start_time = datetime.utcnow()
            cleaning.end_time = datetime.utcnow() + timedelta(hours=cleaning.duration_hours)
            cleaning.start_moisture = float(request.form['start_moisture'])
            cleaning.water_added_liters = float(request.form.get('water_added', 0))
            cleaning.operator_name = request.form['operator_name']
            cleaning.status = 'running'
            
            # Handle file uploads
            if 'start_photo' in request.files:
                file = request.files['start_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"cleaning12h_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cleaning.start_photo = filename
            
            db.session.add(cleaning)
            
            # Update job status
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'{cleaning.duration_hours}-hour cleaning process with target moisture {cleaning.target_moisture}% started!', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting cleaning process: {str(e)}', 'error')
    
    return render_template('cleaning_12h_execution.html', job=job)

# Order Tracking
@app.route('/order_tracking')
def order_tracking():
    order_number = request.args.get('order_number')
    if not order_number:
        flash('Please provide an order number to search.', 'error')
        return redirect(url_for('production_execution'))
    
    order = ProductionOrder.query.filter_by(order_number=order_number).first()
    if not order:
        flash(f'Order {order_number} not found.', 'error')
        return redirect(url_for('production_execution'))
    
    # Get all jobs for this order
    jobs = ProductionJobNew.query.filter_by(order_id=order.id).order_by(ProductionJobNew.created_at.asc()).all()
    
    # Get detailed process data for each job
    job_details = []
    for job in jobs:
        details = {
            'job': job,
            'transfers': ProductionTransfer.query.filter_by(job_id=job.id).all(),
            'cleaning_processes': CleaningProcess.query.filter_by(job_id=job.id).all(),
            'grinding_processes': GrindingProcess.query.filter_by(job_id=job.id).all()
        }
        job_details.append(details)
    
    return render_template('order_tracking.html', 
                         order=order, 
                         job_details=job_details)

# API Routes for reminders and status
@app.route('/api/check_reminders')
def api_check_reminders():
    reminders = []
    
    # Check machine cleaning reminders
    machines = CleaningMachine.query.all()
    for machine in machines:
        if machine.last_cleaned:
            time_since_cleaned = datetime.utcnow() - machine.last_cleaned
            hours_since_cleaned = time_since_cleaned.total_seconds() / 3600
            
            # 5 minute warning
            if (hours_since_cleaned + (5/60)) >= machine.cleaning_frequency_hours:
                if hours_since_cleaned < machine.cleaning_frequency_hours:
                    reminders.append({
                        'message': f'Machine "{machine.name}" needs cleaning in 5 minutes!',
                        'type': 'warning'
                    })
            
            # 10 minute warning
            elif (hours_since_cleaned + (10/60)) >= machine.cleaning_frequency_hours:
                if hours_since_cleaned < machine.cleaning_frequency_hours:
                    reminders.append({
                        'message': f'Machine "{machine.name}" needs cleaning in 10 minutes!',
                        'type': 'info'
                    })
            
            # Overdue
            elif hours_since_cleaned >= machine.cleaning_frequency_hours:
                reminders.append({
                    'message': f'Machine "{machine.name}" cleaning is overdue!',
                    'type': 'danger'
                })
    
    # Check cleaning process completions
    ending_processes = CleaningProcess.query.filter(
        CleaningProcess.status == 'running',
        CleaningProcess.end_time <= datetime.utcnow() + timedelta(minutes=30)
    ).all()
    
    for process in ending_processes:
        time_remaining = process.end_time - datetime.utcnow()
        if time_remaining.total_seconds() > 0:
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            if minutes_remaining <= 10:
                reminders.append({
                    'message': f'{process.process_type} cleaning process ending in {minutes_remaining} minutes!',
                    'type': 'warning'
                })
        else:
            reminders.append({
                'message': f'{process.process_type} cleaning process completed! Ready for next stage.',
                'type': 'success'
            })
    
    return jsonify({'reminders': reminders})

@app.route('/api/machine_status')
def api_machine_status():
    machines = []
    overdue_machines = []
    
    for machine in CleaningMachine.query.all():
        if machine.last_cleaned:
            time_since_cleaned = datetime.utcnow() - machine.last_cleaned
            hours_since_cleaned = time_since_cleaned.total_seconds() / 3600
            
            if hours_since_cleaned < machine.cleaning_frequency_hours:
                status_class = 'status-clean'
            elif hours_since_cleaned < machine.cleaning_frequency_hours * 1.2:
                status_class = 'status-needs-cleaning'
            else:
                status_class = 'status-overdue'
                overdue_machines.append(machine)
        else:
            status_class = 'status-overdue'
            overdue_machines.append(machine)
        
        machines.append({
            'id': machine.id,
            'name': machine.name,
            'status_class': status_class
        })
    
    return jsonify({
        'machines': machines,
        'overdue_machines': [{'id': m.id, 'name': m.name} for m in overdue_machines]
    })

# Machine Cleaning Management
@app.route('/production_execution/machine_cleaning/<int:machine_id>', methods=['GET', 'POST'])
def machine_cleaning_execution(machine_id):
    machine = CleaningMachine.query.get_or_404(machine_id)
    
    if request.method == 'POST':
        try:
            # Create cleaning log
            cleaning_log = CleaningLog()
            cleaning_log.machine_id = machine_id
            cleaning_log.cleaned_by = request.form['cleaned_by']
            cleaning_log.waste_collected = float(request.form.get('waste_collected', 0))
            cleaning_log.notes = request.form.get('notes', '')
            
            # Handle photo uploads
            if 'photo_before' in request.files:
                file = request.files['photo_before']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"cleaning_before_{machine.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cleaning_log.photo_before = filename
            
            if 'photo_after' in request.files:
                file = request.files['photo_after']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"cleaning_after_{machine.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cleaning_log.photo_after = filename
            
            # Update machine last cleaned time
            machine.last_cleaned = datetime.utcnow()
            
            db.session.add(cleaning_log)
            db.session.commit()
            
            flash(f'Machine "{machine.name}" cleaning completed successfully!', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording machine cleaning: {str(e)}', 'error')
    
    # Get cleaning history for this machine
    cleaning_logs = CleaningLog.query.filter_by(machine_id=machine_id).order_by(CleaningLog.cleaning_time.desc()).limit(10).all()
    
    return render_template('machine_cleaning.html', 
                         machine=machine, 
                         cleaning_logs=cleaning_logs)

# Grinding Process
@app.route('/production_execution/grinding/<int:job_id>', methods=['GET', 'POST'])
def grinding_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            # Create grinding process record
            grinding = GrindingProcess()
            grinding.job_id = job_id
            grinding.machine_name = request.form['machine_name']
            grinding.input_quantity_kg = float(request.form['input_quantity'])
            grinding.total_output_kg = float(request.form['total_output'])
            grinding.main_products_kg = float(request.form['main_products'])
            grinding.bran_kg = float(request.form['bran'])
            grinding.bran_percentage = (grinding.bran_kg / grinding.total_output_kg) * 100 if grinding.total_output_kg > 0 else 0
            grinding.operator_name = request.form['operator_name']
            grinding.start_time = datetime.utcnow()
            grinding.status = 'completed'
            
            # Handle file uploads
            if 'start_photo' in request.files:
                file = request.files['start_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"grinding_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    grinding.start_photo = filename
            
            if 'end_photo' in request.files:
                file = request.files['end_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"grinding_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    grinding.end_photo = filename
            
            db.session.add(grinding)
            
            # Check bran percentage
            if grinding.bran_percentage > 25:
                flash(f'Warning: Bran percentage is {grinding.bran_percentage:.1f}% (should be 23-25%)', 'warning')
            
            # Complete current job and create packing job
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = grinding.operator_name
            
            # Create packing job
            packing_job = ProductionJobNew()
            packing_job.order_id = job.order_id
            packing_job.plan_id = job.plan_id
            packing_job.job_number = generate_job_id()
            packing_job.stage = 'packing'
            packing_job.status = 'pending'
            
            db.session.add(packing_job)
            db.session.commit()
            
            flash('Grinding process completed successfully! Packing job created.', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing grinding process: {str(e)}', 'error')
    
    return render_template('grinding_execution.html', job=job)

# Packing Process
@app.route('/production_execution/packing/<int:job_id>', methods=['GET', 'POST'])
def packing_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            # Create packing process records
            products_data = request.form.getlist('product_id')
            bag_weights = request.form.getlist('bag_weight')
            bag_counts = request.form.getlist('bag_count')
            shallow_storage = request.form.getlist('shallow_storage')
            storage_areas = request.form.getlist('storage_area_id')
            
            total_packed = 0
            
            for i in range(len(products_data)):
                if products_data[i] and bag_weights[i] and bag_counts[i]:
                    packing = PackingProcess()
                    packing.job_id = job_id
                    packing.product_id = int(products_data[i])
                    packing.bag_weight_kg = float(bag_weights[i])
                    packing.number_of_bags = int(bag_counts[i])
                    packing.total_packed_kg = packing.bag_weight_kg * packing.number_of_bags
                    packing.stored_in_shallow_kg = float(shallow_storage[i]) if shallow_storage[i] else 0
                    packing.storage_area_id = int(storage_areas[i]) if storage_areas[i] else None
                    packing.operator_name = request.form['operator_name']
                    
                    # Update storage area stock
                    if packing.storage_area_id:
                        storage_area = StorageArea.query.get(packing.storage_area_id)
                        if storage_area:
                            storage_area.current_stock_kg += packing.total_packed_kg + packing.stored_in_shallow_kg
                    
                    total_packed += packing.total_packed_kg + packing.stored_in_shallow_kg
                    db.session.add(packing)
            
            # Handle packing photo
            if 'packing_photo' in request.files:
                file = request.files['packing_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"packing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Update all packing records with the same photo
                    for packing in PackingProcess.query.filter_by(job_id=job_id).all():
                        packing.packing_photo = filename
            
            # Complete job
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = request.form['operator_name']
            
            db.session.commit()
            
            flash(f'Packing completed successfully! Total packed: {total_packed:.2f} kg', 'success')
            return redirect(url_for('production_execution'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing packing process: {str(e)}', 'error')
    
    products = Product.query.filter_by(category='Main Product').all()
    storage_areas = StorageArea.query.all()
    
    return render_template('packing_execution.html', 
                         job=job, 
                         products=products,
                         storage_areas=storage_areas)





@app.route('/production_planning', methods=['GET', 'POST'])
@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id=None):
    order = None
    existing_plan = None
    precleaning_bins = []
    
    if order_id:
        order = ProductionOrder.query.get_or_404(order_id)
        existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
        precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
        
        if request.method == 'POST' and not existing_plan:
            try:
                # Create production plan for specific order
                plan = ProductionPlan()
                plan.order_id = order_id
                plan.planned_by = request.form['planned_by']
                db.session.add(plan)
                db.session.flush()  # Get the plan ID
                
                total_percentage = 0
                precleaning_bin_ids = request.form.getlist('precleaning_bin_id')
                percentages = request.form.getlist('percentage')
                
                for i, bin_id in enumerate(precleaning_bin_ids):
                    if bin_id and i < len(percentages) and percentages[i]:
                        percentage = float(percentages[i])
                        quantity = (percentage / 100) * order.quantity
                        
                        plan_item = ProductionPlanItem()
                        plan_item.plan_id = plan.id
                        plan_item.precleaning_bin_id = int(bin_id)
                        plan_item.percentage = percentage
                        plan_item.quantity = quantity
                        db.session.add(plan_item)
                        total_percentage += percentage
                
                if abs(total_percentage - 100) > 0.1:
                    flash('Total percentage must equal 100%!', 'error')
                    db.session.rollback()
                    return redirect(url_for('production_planning', order_id=order_id))
                
                plan.total_percentage = total_percentage
                plan.status = 'approved'
                order.status = 'planned'
                
                db.session.commit()
                flash('Production plan created successfully!', 'success')
                return redirect(url_for('production_orders'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating production plan: {str(e)}', 'error')
        
        return render_template('production_planning.html', 
                             order=order, 
                             precleaning_bins=precleaning_bins, 
                             existing_plan=existing_plan)
    else:
        # General planning page
        if request.method == 'POST':
            try:
                plan = ProductionPlan()
                plan.order_id = int(request.form['order_id'])
                plan.stage_1_bin_id = request.form.get('stage_1_bin_id')
                plan.stage_1_percentage = float(request.form.get('stage_1_percentage', 0))
                plan.stage_2_bin_id = request.form.get('stage_2_bin_id')
                plan.stage_2_percentage = float(request.form.get('stage_2_percentage', 0))
                plan.stage_3_bin_id = request.form.get('stage_3_bin_id')
                plan.stage_3_percentage = float(request.form.get('stage_3_percentage', 0))
                plan.priority = request.form.get('priority', 'normal')
                plan.status = 'draft'
                
                db.session.add(plan)
                db.session.commit()
                flash('Production plan created successfully!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating plan: {str(e)}', 'error')
        
        orders = ProductionOrder.query.filter_by(status='pending').all()
        bins = PrecleaningBin.query.all()
        plans = ProductionPlan.query.order_by(ProductionPlan.planning_date.desc()).all()
        
        return render_template('production_planning.html', orders=orders, bins=bins, plans=plans)

@app.route('/sales_dispatch', methods=['GET', 'POST'])
def sales_dispatch():
    if request.method == 'POST':
        try:
            dispatch = SalesDispatch()
            dispatch.order_id = int(request.form['order_id'])
            dispatch.customer_id = int(request.form['customer_id'])
            dispatch.product_id = int(request.form['product_id'])
            dispatch.quantity = float(request.form['quantity'])
            dispatch.dispatch_date = datetime.strptime(request.form['dispatch_date'], '%Y-%m-%d')
            dispatch.vehicle_number = request.form['vehicle_number']
            dispatch.driver_name = request.form['driver_name']
            dispatch.notes = request.form.get('notes')
            
            db.session.add(dispatch)
            db.session.commit()
            flash('Dispatch record created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating dispatch: {str(e)}', 'error')
    
    completed_orders = ProductionOrder.query.filter_by(status='completed').all()
    customers = Customer.query.all()
    products = Product.query.all()
    dispatches = SalesDispatch.query.order_by(SalesDispatch.created_at.desc()).limit(20).all()
    
    return render_template('sales_dispatch.html', 
                         orders=completed_orders, 
                         customers=customers, 
                         products=products, 
                         dispatches=dispatches)

@app.route('/reports')
def reports():
    # Generate basic reports data
    total_vehicles = Vehicle.query.count()
    total_stock = db.session.query(db.func.sum(Godown.current_stock)).scalar() or 0
    active_jobs = ProductionJobNew.query.filter_by(status='in_progress').count()
    completed_orders = ProductionOrder.query.filter_by(status='completed').count()
    
    return render_template('reports.html',
                         total_vehicles=total_vehicles,
                         total_stock=total_stock,
                         active_jobs=active_jobs,
                         completed_orders=completed_orders)

@app.route('/cleaning_management', methods=['GET', 'POST'])
def cleaning_management():
    if request.method == 'POST':
        try:
            cleaning = CleaningProcess()
            cleaning.machine_name = request.form['machine_name']
            cleaning.cleaning_type = request.form['cleaning_type']
            cleaning.operator = request.form['operator']
            cleaning.start_time = datetime.now()
            cleaning.status = 'in_progress'
            cleaning.notes = request.form.get('notes')
            
            db.session.add(cleaning)
            db.session.commit()
            flash('Cleaning process started!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting cleaning: {str(e)}', 'error')
    
    active_cleanings = CleaningProcess.query.filter_by(status='in_progress').all()
    recent_cleanings = CleaningProcess.query.order_by(CleaningProcess.created_at.desc()).limit(10).all()
    
    return render_template('cleaning_management.html',
                         active_cleanings=active_cleanings,
                         recent_cleanings=recent_cleanings)

@app.route('/masters', methods=['GET', 'POST'])
def masters():
    if request.method == 'POST':
        try:
            form_type = request.form.get('form_type')
            
            if form_type == 'supplier':
                supplier = Supplier()
                supplier.company_name = request.form['company_name']
                supplier.contact_person = request.form.get('contact_person')
                supplier.phone = request.form.get('phone')
                supplier.address = request.form.get('address')
                supplier.city = request.form.get('city')
                supplier.state = request.form.get('state')
                supplier.postal_code = request.form.get('postal_code')
                
                db.session.add(supplier)
                db.session.commit()
                flash('Supplier added successfully!', 'success')
                
            elif form_type == 'customer':
                customer = Customer()
                customer.company_name = request.form['company_name']
                customer.contact_person = request.form.get('contact_person')
                customer.phone = request.form.get('phone')
                customer.email = request.form.get('email')
                customer.address = request.form.get('address')
                customer.city = request.form.get('city')
                customer.state = request.form.get('state')
                customer.postal_code = request.form.get('postal_code')
                
                db.session.add(customer)
                db.session.commit()
                flash('Customer added successfully!', 'success')
                
            elif form_type == 'product':
                product = Product()
                product.name = request.form['name']
                product.category = request.form['category']
                product.description = request.form.get('description')
                
                db.session.add(product)
                db.session.commit()
                flash('Product added successfully!', 'success')
                
            elif form_type == 'godown':
                godown = Godown()
                godown.name = request.form['name']
                godown.type_id = int(request.form['type_id'])
                godown.capacity = float(request.form['capacity'])
                
                db.session.add(godown)
                db.session.commit()
                flash('Godown added successfully!', 'success')
                
            elif form_type == 'precleaning_bin':
                bin_obj = PrecleaningBin()
                bin_obj.name = request.form['name']
                bin_obj.capacity = float(request.form['capacity'])
                
                db.session.add(bin_obj)
                db.session.commit()
                flash('Pre-cleaning bin added successfully!', 'success')
                
            return redirect(url_for('masters'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding record: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    godown_types = GodownType.query.all()
    godowns = Godown.query.join(GodownType).all()
    precleaning_bins = PrecleaningBin.query.all()
    
    return render_template('masters.html',
                         suppliers=suppliers,
                         customers=customers,
                         products=products,
                         godown_types=godown_types,
                         godowns=godowns,
                         precleaning_bins=precleaning_bins)

@app.route('/api/quality_test/<int:test_id>')
def get_quality_test_details(test_id):
    """API endpoint to get quality test details"""
    try:
        test = QualityTest.query.get_or_404(test_id)
        return jsonify({
            'id': test.id,
            'vehicle_number': test.vehicle.vehicle_number,
            'supplier_name': test.vehicle.supplier.company_name if test.vehicle.supplier else None,
            'test_time': test.test_time.strftime('%d/%m/%Y %H:%M'),
            'lab_instructor': test.lab_instructor,
            'sample_bags_tested': test.sample_bags_tested,
            'total_bags': test.total_bags,
            'moisture_content': test.moisture_content,
            'category_assigned': test.category_assigned,
            'approved': test.approved,
            'quality_notes': test.quality_notes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers')
def get_customers():
    """API endpoint to get customers data for dropdowns"""
    try:
        customers = Customer.query.all()
        return jsonify([{
            'id': customer.id,
            'company_name': customer.company_name,
            'contact_person': customer.contact_person,
            'phone': customer.phone
        } for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def get_products():
    """API endpoint to get products data for dropdowns"""
    try:
        products = Product.query.filter_by(category='Main Product').all()
        return jsonify([{
            'id': product.id,
            'name': product.name,
            'category': product.category
        } for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_job', methods=['POST'])
def api_start_job():
    """API endpoint to start a production job"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        job = ProductionJobNew.query.get_or_404(job_id)
        job.status = 'in_progress'
        job.started_at = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Job started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/pause_job', methods=['POST'])
def api_pause_job():
    """API endpoint to pause a production job"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        job = ProductionJobNew.query.get_or_404(job_id)
        job.status = 'paused'
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Job paused successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/production_job/<int:job_id>')
def api_get_production_job(job_id):
    """API endpoint to get production job details"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)
        return jsonify({
            'id': job.id,
            'job_number': job.job_number,
            'order_number': job.plan.order.order_number if job.plan and job.plan.order else 'N/A',
            'stage': job.stage,
            'status': job.status,
            'progress': 50,  # Default progress
            'timeline': []  # Add timeline data as needed
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job_details/<int:job_id>')
def api_job_details(job_id):
    """Get detailed information about a job for modal display"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)
        order = ProductionOrder.query.get(job.order_id) if job.order_id else None
        
        job_data = {
            'id': job.id,
            'job_number': job.job_number,
            'order_number': order.order_number if order else 'N/A',
            'stage': job.stage.replace('_', ' ').title(),
            'status': job.status,
            'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else None,
            'started_by': job.started_by,
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else None,
            'completed_by': job.completed_by,
            'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else None
        }
        
        return jsonify({'success': True, 'job': job_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/job_progress')
def api_job_progress():
    """API endpoint to get job progress updates"""
    try:
        jobs = ProductionJobNew.query.filter(ProductionJobNew.status.in_(['in_progress', 'pending'])).all()
        return jsonify([{
            'id': job.id,
            'progress': 75 if job.status == 'in_progress' else 0
        } for job in jobs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Removed duplicate route - using the comprehensive one above

@app.route('/init_data')
def init_data():
    """Initialize sample data for the application"""
    try:
        from app import init_sample_data
        init_sample_data()
        flash('Sample data initialized successfully!', 'success')
    except Exception as e:
        flash(f'Error initializing data: {str(e)}', 'error')
    return redirect(url_for('index'))