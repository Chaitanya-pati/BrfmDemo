import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

from app import app, db
from models import (Vehicle, Supplier, Godown, GodownType, QualityTest, Transfer, 
                   PrecleaningBin, ProductionOrder, ProductionPlan, ProductionJobNew,
                   Customer, Product, SalesDispatch, CleaningProcess)
from utils import allowed_file, generate_order_number

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
            
            # Create quality test record
            quality_test = QualityTest()
            quality_test.vehicle_id = vehicle_id
            quality_test.moisture_content = float(request.form['moisture_content'])
            quality_test.foreign_matter = float(request.form['foreign_matter'])
            quality_test.broken_grains = float(request.form['broken_grains'])
            quality_test.test_result = request.form['test_result']
            quality_test.tested_by = request.form['tested_by']
            quality_test.notes = request.form.get('notes')
            
            # Update vehicle with quality info
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
            production_order.customer = request.form['customer']
            production_order.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
            production_order.priority = request.form.get('priority', 'normal')
            production_order.notes = request.form.get('notes')
            
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
                job = ProductionJobNew()
                job.plan_id = int(request.form['plan_id'])
                job.job_number = generate_order_number('JOB')
                job.stage = request.form['stage']
                job.started_by = request.form['operator_name']
                job.status = 'in_progress'
                job.started_at = datetime.now()
                job.notes = request.form.get('notes')
                
                db.session.add(job)
                db.session.commit()
                flash('Production job started successfully!', 'success')
                
            elif action == 'execute_transfer':
                # Handle transfer execution
                job_id = request.form['job_id']
                from_bin_id = request.form['from_bin_id']
                quantity = float(request.form['transfer_quantity'])
                to_bin = request.form['to_cleaning_bin']
                
                # Create transfer record
                transfer = Transfer()
                transfer.from_precleaning_bin_id = int(from_bin_id)
                transfer.quantity = quantity
                transfer.transfer_type = 'precleaning_to_cleaning'
                transfer.operator = request.form['operator_name']
                
                db.session.add(transfer)
                db.session.commit()
                flash('Transfer executed successfully!', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing request: {str(e)}', 'error')
    
    # Get data for template
    active_jobs = ProductionJobNew.query.filter(ProductionJobNew.status.in_(['pending', 'in_progress'])).all()
    approved_plans = ProductionPlan.query.filter_by(status='approved').all()
    transfer_jobs = ProductionJobNew.query.filter_by(stage='transfer').all()
    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    pending_reminders = []  # This would come from a reminders system
    
    return render_template('production_execution.html',
                         active_jobs=active_jobs,
                         approved_plans=approved_plans,
                         transfer_jobs=transfer_jobs,
                         precleaning_bins=precleaning_bins,
                         pending_reminders=pending_reminders)

@app.route('/production_planning', methods=['GET', 'POST'])
def production_planning():
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
    plans = ProductionPlan.query.order_by(ProductionPlan.created_at.desc()).all()
    
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

@app.route('/masters')
def masters():
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    godown_types = GodownType.query.all()
    
    return render_template('masters.html',
                         suppliers=suppliers,
                         customers=customers,
                         products=products,
                         godown_types=godown_types)