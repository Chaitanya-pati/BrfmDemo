import os
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import *

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_order_number(prefix='ORD'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{timestamp}"

@app.route('/')
def index():
    # Dashboard data
    pending_vehicles = Vehicle.query.filter_by(status='pending').count()
    quality_check_vehicles = Vehicle.query.filter_by(status='quality_check').count()
    active_orders = ProductionOrder.query.filter(ProductionOrder.status.in_(['pending', 'planned', 'in_progress'])).count()
    pending_dispatches = Dispatch.query.filter_by(status='loaded').count()
    
    # Recent activities
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    recent_orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         pending_vehicles=pending_vehicles,
                         quality_check_vehicles=quality_check_vehicles,
                         active_orders=active_orders,
                         pending_dispatches=pending_dispatches,
                         recent_vehicles=recent_vehicles,
                         recent_orders=recent_orders)

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
            quality_test.lab_instructor = request.form['lab_instructor']
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

@app.route('/weight_entry', methods=['GET', 'POST'])
def weight_entry():
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            vehicle = Vehicle.query.get_or_404(vehicle_id)
            
            if 'vehicle_photo_after' in request.files:
                file = request.files['vehicle_photo_after']
                if file and file.filename and allowed_file(file.filename):
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
            # Handle transfer photos
            transfer_photo = None
            
            if 'transfer_photo' in request.files:
                file = request.files['transfer_photo']
                if file and file.filename and allowed_file(file.filename):
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
            order = ProductionOrder()
            order.order_number = generate_order_number('PO')
            
            # Handle customer field - check if it's customer_id or customer name
            if request.form.get('customer_id'):
                order.customer_id = int(request.form['customer_id'])
            elif request.form.get('customer'):
                # If customer name is provided, find or create customer
                customer_name = request.form['customer']
                customer = Customer.query.filter_by(company_name=customer_name).first()
                if customer:
                    order.customer_id = customer.id
                else:
                    # Create new customer with minimal info
                    new_customer = Customer(company_name=customer_name)
                    db.session.add(new_customer)
                    db.session.flush()
                    order.customer_id = new_customer.id
            
            order.quantity = float(request.form['quantity'])
            
            # Handle product field - check if it's product_id or product name
            if request.form.get('product_id'):
                product = Product.query.get(int(request.form['product_id']))
                order.product = product.name if product else 'Unknown Product'
            elif request.form.get('product'):
                order.product = request.form['product']
            
            order.finished_good_type = request.form.get('finished_good_type')
            order.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d') if request.form.get('deadline') else None
            order.priority = request.form.get('priority', 'normal')
            order.description = request.form.get('notes')  # Map notes to description
            order.created_by = request.form.get('created_by', 'System')
            order.target_completion = datetime.strptime(request.form['target_completion'], '%Y-%m-%d') if request.form.get('target_completion') else None
            
            db.session.add(order)
            db.session.commit()
            flash('Production order created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Production order creation error: {str(e)}")  # Debug print
            flash(f'Error creating production order: {str(e)}', 'error')
    
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    customers = Customer.query.all()
    products = Product.query.filter_by(category='Main Product').all()
    
    return render_template('production_orders.html', orders=orders, customers=customers, products=products)

@app.route('/production_planning')
@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id=None):
    order = None
    existing_plan = None
    
    if order_id:
        order = ProductionOrder.query.get_or_404(order_id)
        existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
    
    if request.method == 'POST' and order:
        try:
            # Create production plan
            plan = ProductionPlan()
            plan.order_id = order_id
            plan.planned_by = request.form['planned_by']
            db.session.add(plan)
            db.session.flush()  # Get the plan ID
            
            total_percentage = 0
            precleaning_bins = request.form.getlist('precleaning_bin_id')
            percentages = request.form.getlist('percentage')
            
            for i, bin_id in enumerate(precleaning_bins):
                if bin_id and percentages[i]:
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
    
    # Data for template
    orders = ProductionOrder.query.filter_by(status='pending').all()
    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    bins = precleaning_bins  # For sidebar display
    plans = ProductionPlan.query.order_by(ProductionPlan.planning_date.desc()).limit(10).all()
    products = Product.query.filter_by(category='Main Product').all()
    
    return render_template('production_planning.html', 
                         order=order, 
                         orders=orders, 
                         precleaning_bins=precleaning_bins,
                         bins=bins, 
                         plans=plans, 
                         products=products,
                         existing_plan=existing_plan)

@app.route('/reports')
def reports():
    # Various report data
    vehicle_stats = db.session.query(
        Vehicle.status, 
        db.func.count(Vehicle.id).label('count')
    ).group_by(Vehicle.status).all()
    
    godown_inventory = Godown.query.join(GodownType).all()
    
    production_stats = db.session.query(
        ProductionOrder.status,
        db.func.count(ProductionOrder.id).label('count')
    ).group_by(ProductionOrder.status).all()
    
    return render_template('reports.html', 
                         vehicle_stats=vehicle_stats,
                         godown_inventory=godown_inventory,
                         production_stats=production_stats)

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

@app.route('/godown_management')
def godown_management():
    godowns = Godown.query.join(GodownType).all()
    godown_types = GodownType.query.all()
    
    return render_template('godown_management.html', godowns=godowns, godown_types=godown_types)

@app.route('/cleaning_management', methods=['GET', 'POST'])
def cleaning_management():
    if request.method == 'POST':
        try:
            # Handle photo uploads
            photo_before = None
            photo_after = None
            
            if 'photo_before' in request.files:
                file = request.files['photo_before']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"before_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photo_before = filename
            
            if 'photo_after' in request.files:
                file = request.files['photo_after']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"after_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photo_after = filename
            
            cleaning_log = CleaningLog()
            cleaning_log.machine_id = int(request.form['machine_id'])
            cleaning_log.cleaned_by = request.form['cleaned_by']
            cleaning_log.photo_before = photo_before
            cleaning_log.photo_after = photo_after
            cleaning_log.waste_collected = float(request.form.get('waste_collected', 0))
            cleaning_log.notes = request.form.get('notes')
            
            # Update machine's last cleaned time
            machine = CleaningMachine.query.get(request.form['machine_id'])
            if machine:
                machine.last_cleaned = datetime.now()
            
            db.session.add(cleaning_log)
            db.session.commit()
            flash('Cleaning log recorded successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording cleaning log: {str(e)}', 'error')
    
    machines = CleaningMachine.query.all()
    recent_logs = CleaningLog.query.join(CleaningMachine).order_by(CleaningLog.cleaning_time.desc()).limit(20).all()
    
    # Check for machines due for cleaning
    due_machines = []
    for machine in machines:
        if machine.last_cleaned:
            next_cleaning = machine.last_cleaned + timedelta(hours=machine.cleaning_frequency_hours)
            if datetime.now() >= next_cleaning:
                due_machines.append(machine)
        else:
            due_machines.append(machine)  # Never cleaned
    
    return render_template('cleaning_management.html', machines=machines, cleaning_logs=recent_logs, due_machines=due_machines)

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
        vehicle.owner_approved = False
        db.session.commit()
        flash('Vehicle rejected!', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting vehicle: {str(e)}', 'error')
    return redirect(url_for('quality_control'))

@app.route('/production_tracking')
def production_tracking():
    """General production tracking overview with links to detailed views"""
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).limit(20).all()
    
    # Build tracking data for each order
    tracking_data = []
    for order in orders:
        jobs = ProductionJobNew.query.filter_by(order_id=order.id).all()
        plan = ProductionPlan.query.filter_by(order_id=order.id).first()
        
        order_data = {
            'order': order,
            'plan': plan,
            'jobs': jobs,
            'total_jobs': len(jobs),
            'completed_jobs': len([j for j in jobs if j.status == 'completed']),
            'in_progress_jobs': len([j for j in jobs if j.status == 'in_progress']),
            'pending_jobs': len([j for j in jobs if j.status == 'pending'])
        }
        tracking_data.append(order_data)
    
    return render_template('production_tracking.html', tracking_data=tracking_data)

@app.route('/machine_cleaning')
def machine_cleaning():
    """General machine cleaning overview"""
    machines = CleaningMachine.query.all()
    
    # Get recent cleaning logs
    recent_logs = MachineCleaningLog.query.join(ProductionMachine).order_by(MachineCleaningLog.cleaning_start_time.desc()).limit(20).all()
    
    # Get in-progress cleanings
    in_progress = MachineCleaningLog.query.filter_by(status='in_progress').all()
    
    # Check for machines due for cleaning
    due_machines = []
    for machine in machines:
        if machine.last_cleaned:
            next_cleaning = machine.last_cleaned + timedelta(hours=machine.cleaning_frequency_hours)
            if datetime.now() >= next_cleaning:
                due_machines.append(machine)
        else:
            due_machines.append(machine)  # Never cleaned
    
    return render_template('machine_cleaning_overview.html', 
                         machines=machines, 
                         recent_logs=recent_logs,
                         in_progress=in_progress, 
                         due_machines=due_machines)

@app.route('/storage_management')
def storage_management():
    """Storage and finished goods management"""
    storage_areas = StorageArea.query.all()
    finished_goods = FinishedGoods.query.order_by(FinishedGoods.created_at.desc()).limit(50).all()
    
    # Calculate storage utilization
    total_capacity = sum([area.capacity_kg for area in storage_areas])
    total_current = sum([area.current_stock_kg for area in storage_areas])
    utilization_percent = (total_current / total_capacity * 100) if total_capacity > 0 else 0
    
    return render_template('storage_management.html', 
                         storage_areas=storage_areas,
                         finished_goods=finished_goods,
                         total_capacity=total_capacity,
                         total_current=total_current,
                         utilization_percent=utilization_percent)

@app.route('/init_data')
def init_data():
    """Initialize sample data for testing"""
    try:
        # Create sample suppliers if none exist
        if Supplier.query.count() == 0:
            suppliers = [
                Supplier(name='ABC Farm Supplies', contact_person='John Doe', phone='9876543210', address='Sample Address 1'),
                Supplier(name='XYZ Agricultural Co.', contact_person='Jane Smith', phone='9876543211', address='Sample Address 2')
            ]
            for supplier in suppliers:
                db.session.add(supplier)
        
        # Create sample customers if none exist
        if Customer.query.count() == 0:
            customers = [
                Customer(name='Sample Customer 1', contact_person='Customer Rep 1', phone='9876543212', address='Customer Address 1'),
                Customer(name='Sample Customer 2', contact_person='Customer Rep 2', phone='9876543213', address='Customer Address 2')
            ]
            for customer in customers:
                db.session.add(customer)
        
        # Create sample products if none exist
        if Product.query.count() == 0:
            products = [
                Product(name='Wheat Flour', category='Main Product', unit='kg', standard_price=50.0),
                Product(name='Wheat Bran', category='By-product', unit='kg', standard_price=25.0),
                Product(name='Fine Flour', category='Main Product', unit='kg', standard_price=55.0)
            ]
            for product in products:
                db.session.add(product)
        
        db.session.commit()
        flash('Sample data initialized successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error initializing data: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/production_execution', methods=['GET', 'POST'])
def production_execution():
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'start_job':
                # Start a new production job
                plan_id = int(request.form['plan_id'])
                stage = request.form['stage']
                operator_name = request.form['operator_name']
                notes = request.form.get('notes', '')
                
                plan = ProductionPlan.query.get_or_404(plan_id)
                
                # Generate unique job number
                job_number = f"JOB{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                job = ProductionJobNew()
                job.job_number = job_number
                job.order_id = plan.order_id
                job.plan_id = plan_id
                job.stage = stage
                job.status = 'pending'
                job.started_by = operator_name
                job.notes = notes
                job.created_at = datetime.now()
                
                db.session.add(job)
                db.session.commit()
                
                flash(f'Production job {job_number} started successfully!', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing request: {str(e)}', 'error')
    
    # Get data for template
    active_jobs = ProductionJobNew.query.filter(ProductionJobNew.status.in_(['pending', 'in_progress'])).all()
    approved_plans = ProductionPlan.query.filter_by(status='approved').all()
    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    
    return render_template('production_execution.html',
                         active_jobs=active_jobs,
                         approved_plans=approved_plans,
                         precleaning_bins=precleaning_bins)

@app.route('/packing_execution/<int:job_id>', methods=['GET', 'POST'])
def packing_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    # Check for grinding process in this job or related grinding jobs
    grinding_process = GrindingProcess.query.filter_by(job_id=job_id).first()
    if not grinding_process:
        # Look for grinding process in other jobs with the same order_id
        related_jobs = ProductionJobNew.query.filter_by(order_id=job.order_id, stage='grinding').all()
        for related_job in related_jobs:
            grinding_process = GrindingProcess.query.filter_by(job_id=related_job.id).first()
            if grinding_process:
                break
    
    if not grinding_process:
        flash('Grinding process must be completed before packing!', 'error')
        return redirect(url_for('production_execution'))

    if request.method == 'POST':
        try:
            if request.form.get('action') == 'pack_products':
                operator = request.form['operator_name']
                
                # Handle photo upload
                packing_photo = None
                if 'packing_photo' in request.files:
                    file = request.files['packing_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"packing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        packing_photo = filename

                # Process all products from the form (handle multiple products)
                product_ids = request.form.getlist('product_id')
                bag_weights = request.form.getlist('bag_weight')
                bag_counts = request.form.getlist('bag_count')
                storage_area_ids = request.form.getlist('storage_area_id')
                shallow_storages = request.form.getlist('shallow_storage')
                
                total_packed_count = 0
                
                for i in range(len(product_ids)):
                    if product_ids[i] and bag_weights[i] and bag_counts[i]:
                        product_id = int(product_ids[i])
                        bag_weight = float(bag_weights[i])
                        number_of_bags = int(bag_counts[i])
                        storage_area_id = storage_area_ids[i] if i < len(storage_area_ids) and storage_area_ids[i] else None
                        stored_in_shallow = float(shallow_storages[i]) if i < len(shallow_storages) and shallow_storages[i] else 0
                        
                        # Create packing process
                        packing = PackingProcess()
                        packing.job_id = job_id
                        packing.product_id = product_id
                        packing.bag_weight_kg = bag_weight
                        packing.number_of_bags = number_of_bags
                        packing.total_packed_kg = bag_weight * number_of_bags
                        packing.operator_name = operator
                        packing.storage_area_id = int(storage_area_id) if storage_area_id else None
                        packing.stored_in_shallow_kg = stored_in_shallow
                        packing.packing_photo = packing_photo
                        
                        # Update storage area stock if selected
                        if storage_area_id:
                            storage_area = StorageArea.query.get(int(storage_area_id))
                            if storage_area:
                                storage_area.current_stock_kg += packing.total_packed_kg
                        
                        db.session.add(packing)
                        
                        # Create finished goods entry - THIS IS THE FIX FOR FINISHED GOODS DATA
                        finished_goods = FinishedGoods()
                        finished_goods.order_id = job.order_id
                        finished_goods.product_id = product_id
                        finished_goods.quantity = packing.total_packed_kg
                        finished_goods.storage_type = 'bags'
                        finished_goods.bag_weight = bag_weight
                        finished_goods.bag_count = number_of_bags
                        finished_goods.batch_number = f"BATCH-{job.order.order_number}-{datetime.now().strftime('%Y%m%d')}"
                        
                        db.session.add(finished_goods)
                        total_packed_count += 1
                
                # Mark job as completed
                job.status = 'completed'
                job.completed_at = datetime.now()
                job.completed_by = operator
                
                db.session.commit()
                
                flash(f'Packing process completed successfully! Processed {total_packed_count} products.', 'success')
                return redirect(url_for('production_execution'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error in packing process: {str(e)}', 'error')

    products = Product.query.filter_by(category='Main Product').all()
    storage_areas = StorageArea.query.all()
    existing_packing = PackingProcess.query.filter_by(job_id=job_id).all()
    
    # Get finished goods for this order - THIS FIXES THE DATA DISPLAY
    finished_goods = FinishedGoods.query.filter_by(order_id=job.order_id).all()

    return render_template('packing_execution.html', 
                         job=job, 
                         grinding_process=grinding_process,
                         products=products,
                         storage_areas=storage_areas,
                         existing_packing=existing_packing,
                         finished_goods=finished_goods)

# LIVE PRODUCTION DASHBOARD FOR CONCURRENT OPERATIONS
@app.route('/live_production_dashboard')
def live_production_dashboard():
    """Dashboard showing all concurrent live production operations"""
    
    # Get all active production jobs
    active_jobs = ProductionJobNew.query.filter(
        ProductionJobNew.status.in_(['in_progress', 'pending'])
    ).order_by(ProductionJobNew.created_at.desc()).all()
    
    # Get all running cleaning processes
    running_cleanings = CleaningProcess.query.filter_by(status='running').all()
    
    # Get all active grinding processes
    active_grindings = GrindingProcess.query.filter_by(status='pending').all()
    
    # Get all in-progress machine cleanings
    active_machine_cleanings = MachineCleaningLog.query.filter_by(status='in_progress').all()
    
    # Build live operations data
    live_operations = []
    
    for job in active_jobs:
        operation = {
            'job': job,
            'type': 'production_job',
            'order': job.order,
            'cleaning_processes': CleaningProcess.query.filter_by(job_id=job.id).all(),
            'grinding_processes': GrindingProcess.query.filter_by(job_id=job.id).all(),
            'packing_processes': PackingProcess.query.filter_by(job_id=job.id).all(),
            'machine_cleanings': MachineCleaningLog.query.filter_by(job_id=job.id).all()
        }
        live_operations.append(operation)
    
    # Get concurrent bin operations (multiple bins being used simultaneously)
    concurrent_bins = CleaningBin.query.filter(
        CleaningBin.status.in_(['cleaning', 'occupied'])
    ).all()
    
    return render_template('live_production_dashboard.html',
                         live_operations=live_operations,
                         running_cleanings=running_cleanings,
                         active_grindings=active_grindings,
                         active_machine_cleanings=active_machine_cleanings,
                         concurrent_bins=concurrent_bins)

# PRODUCTION ORDER DETAILS WITH MACHINE CLEANING RECORDS
@app.route('/order_tracking/<order_number>')
def order_tracking_detail(order_number):
    """Display detailed tracking for a specific order"""
    order = ProductionOrder.query.filter_by(order_number=order_number).first_or_404()
    plan = ProductionPlan.query.filter_by(order_id=order.id).first()
    jobs = ProductionJobNew.query.filter_by(order_id=order.id).order_by(ProductionJobNew.created_at).all()

    # Build job details with associated processes INCLUDING MACHINE CLEANING RECORDS
    job_details = []
    for job in jobs:
        # Get machine cleaning logs for this job
        machine_cleanings = MachineCleaningLog.query.filter_by(job_id=job.id).all()
        
        # Get cleaning schedules for this job  
        cleaning_schedules = CleaningSchedule.query.filter_by(job_id=job.id).all()
        
        # Calculate cleaning statistics
        completed_cleanings = [c for c in machine_cleanings if c.status == 'completed']
        total_cleaning_time = sum([c.cleaning_duration_minutes or 0 for c in completed_cleanings])
        
        job_detail = {
            'job': job,
            'transfers': ProductionTransfer.query.filter_by(job_id=job.id).all(),
            'cleaning_processes': CleaningProcess.query.filter_by(job_id=job.id).all(),
            'grinding_processes': GrindingProcess.query.filter_by(job_id=job.id).all(),
            'packing_processes': PackingProcess.query.filter_by(job_id=job.id).all(),
            'machine_cleanings': machine_cleanings,  # MACHINE CLEANING RECORDS INCLUDED
            'cleaning_schedules': cleaning_schedules,
            'cleaning_stats': {
                'total_cleanings': len(completed_cleanings),
                'total_cleaning_time_minutes': total_cleaning_time,
                'pending_cleanings': len([s for s in cleaning_schedules if s.status == 'scheduled']),
                'cancelled_cleanings': len([s for s in cleaning_schedules if s.status == 'cancelled'])
            }
        }
        job_details.append(job_detail)

    return render_template('order_tracking.html', 
                         order=order, 
                         plan=plan, 
                         job_details=job_details)

# MACHINE CLEANING PROCESS WITH PROPER CONTROLS
@app.route('/process_machine_cleaning/<int:job_id>', methods=['GET', 'POST'])
def process_machine_cleaning(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'start_cleaning':
                machine_id = int(request.form['machine_id'])
                
                # Handle before photo upload
                before_photo = None
                if 'before_photo' in request.files:
                    file = request.files['before_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"machine_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        before_photo = filename
                
                # Create cleaning log
                cleaning_log = MachineCleaningLog(
                    machine_id=machine_id,
                    production_order_id=job.order_id,
                    job_id=job_id,
                    process_step=job.stage,
                    cleaned_by=request.form['cleaned_by'],
                    photo_before=before_photo,
                    status='in_progress'
                )
                
                db.session.add(cleaning_log)
                db.session.commit()
                
                flash('Machine cleaning started!', 'success')
                return redirect(url_for('complete_process_machine_cleaning', log_id=cleaning_log.id))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting machine cleaning: {str(e)}', 'error')
    
    # Get machines that need cleaning
    machines = CleaningMachine.query.all()
    
    # Get pending and recent cleaning logs for this job
    pending_cleanings = MachineCleaningLog.query.filter_by(
        job_id=job_id,
        status='scheduled'
    ).all()
    
    recent_logs = MachineCleaningLog.query.filter_by(
        job_id=job_id
    ).order_by(MachineCleaningLog.cleaning_start_time.desc()).limit(10).all()
    
    # Get in-progress cleaning logs for this job
    in_progress_cleanings = MachineCleaningLog.query.filter_by(
        job_id=job_id,
        status='in_progress'
    ).all()
    
    return render_template('process_machine_cleaning.html',
                         job=job,
                         machines=machines,
                         pending_cleanings=pending_cleanings,
                         recent_logs=recent_logs,
                         in_progress_cleanings=in_progress_cleanings)

@app.route('/complete_process_machine_cleaning/<int:log_id>', methods=['GET', 'POST'])
def complete_process_machine_cleaning(log_id):
    log = MachineCleaningLog.query.get_or_404(log_id)
    
    if request.method == 'POST':
        try:
            # Handle after photo upload
            after_photo = None
            if 'after_photo' in request.files:
                file = request.files['after_photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"machine_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    after_photo = filename
            
            # Complete the cleaning log
            log.cleaning_end_time = datetime.now()
            log.photo_after = after_photo
            log.waste_collected_kg = float(request.form.get('waste_collected', 0))
            log.notes = request.form.get('notes', '')
            log.status = 'completed'
            
            # Calculate cleaning duration
            if log.cleaning_start_time:
                duration = log.cleaning_end_time - log.cleaning_start_time
                log.cleaning_duration_minutes = int(duration.total_seconds() / 60)
            
            # Update machine last cleaned time
            if log.machine:
                log.machine.last_cleaned = log.cleaning_end_time
            
            db.session.commit()
            
            flash('Machine cleaning completed successfully!', 'success')
            return redirect(url_for('process_machine_cleaning', job_id=log.job_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing machine cleaning: {str(e)}', 'error')
    
    return render_template('complete_machine_cleaning.html', log=log)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/production_jobs_by_stage')
def api_production_jobs_by_stage():
    """API endpoint to get production jobs grouped by stage"""
    try:
        jobs_by_stage = {
            'cleaning_24h': [],
            'cleaning_12h': [],
            'grinding': [],
            'packing': []
        }
        
        # Get all active jobs
        active_jobs = ProductionJobNew.query.filter(
            ProductionJobNew.status.in_(['pending', 'in_progress'])
        ).all()
        
        for job in active_jobs:
            job_data = {
                'id': job.id,
                'job_number': job.job_number,
                'order_number': job.order.order_number if job.order else 'N/A',
                'status': job.status,
                'stage': job.stage,
                'progress': 0 if job.status == 'pending' else 50 if job.status == 'in_progress' else 100,
                'can_proceed': job.status == 'pending',
                'is_previous_step': False,
                'is_running': job.status == 'in_progress',
                'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
                'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else '',
                'started_by': job.started_by or '',
                'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else '',
                'completed_by': job.completed_by or ''
            }
            
            if job.stage in jobs_by_stage:
                jobs_by_stage[job.stage].append(job_data)
        
        return jsonify({'success': True, 'data': jobs_by_stage})
        
    except Exception as e:
        app.logger.error(f"API Error in production_jobs_by_stage: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/job_details/<int:job_id>')
def api_job_details(job_id):
    """API endpoint to get detailed job information"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)
        
        job_data = {
            'id': job.id,
            'job_number': job.job_number,
            'order_number': job.order.order_number if job.order else 'N/A',
            'status': job.status,
            'stage': job.stage,
            'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
            'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else '',
            'started_by': job.started_by,
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else '',
            'completed_by': job.completed_by,
            'notes': job.notes
        }
        
        return jsonify({'success': True, 'job': job_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/start_production_execution/<int:order_id>')
def start_production_execution(order_id):
    """Start production execution by creating jobs for all stages"""
    try:
        order = ProductionOrder.query.get_or_404(order_id)
        plan = ProductionPlan.query.filter_by(order_id=order_id).first()
        
        if not plan:
            flash('No production plan found for this order!', 'error')
            return redirect(url_for('production_planning', order_id=order_id))
        
        if plan.status != 'approved':
            flash('Production plan must be approved before starting execution!', 'error')
            return redirect(url_for('production_planning', order_id=order_id))
        
        # Check if jobs already exist
        existing_jobs = ProductionJobNew.query.filter_by(order_id=order_id).count()
        if existing_jobs > 0:
            flash('Production jobs already exist for this order!', 'info')
            return redirect(url_for('production_execution'))
        
        # Create jobs for all production stages
        stages = ['transfer', 'cleaning_24h', 'cleaning_12h', 'grinding', 'packing']
        
        for i, stage in enumerate(stages):
            job = ProductionJobNew()
            job.job_number = f"JOB-{order.order_number}-{stage.upper()}-{datetime.now().strftime('%m%d%H%M')}"
            job.order_id = order_id
            job.plan_id = plan.id
            job.stage = stage
            job.status = 'pending'
            job.started_by = 'System'
            job.notes = f'Auto-created job for {stage} stage'
            job.created_at = datetime.now()
            
            db.session.add(job)
        
        # Update order status
        order.status = 'in_progress'
        
        db.session.commit()
        flash('Production execution started! All jobs have been created.', 'success')
        return redirect(url_for('production_execution'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error starting production execution: {str(e)}', 'error')
        return redirect(url_for('production_planning', order_id=order_id))

@app.route('/production_execution/cleaning_setup/<int:job_id>')
def cleaning_setup(job_id):
    """Set up 24-hour cleaning process"""
    job = ProductionJobNew.query.get_or_404(job_id)
    # Get available cleaning bins
    cleaning_bins = CleaningBin.query.filter_by(status='available').all()
    return render_template('cleaning_setup.html', job=job, cleaning_bins=cleaning_bins)

@app.route('/production_execution/cleaning_12h_setup/<int:job_id>')
def cleaning_12h_setup(job_id):
    """Set up 12-hour cleaning process"""
    job = ProductionJobNew.query.get_or_404(job_id)
    return render_template('cleaning_12h_setup.html', job=job)

@app.route('/production_execution/b1_scale/<int:job_id>')
def b1_scale_process(job_id):
    """B1 scale and grinding process"""
    job = ProductionJobNew.query.get_or_404(job_id)
    return render_template('b1_scale_process.html', job=job)

@app.route('/production_execution/packing/<int:job_id>')
def packing_execution_route(job_id):
    """Redirect to existing packing execution"""
    return redirect(url_for('packing_execution', job_id=job_id))

@app.route('/process_cleaning_24h/<int:job_id>', methods=['POST'])
def process_cleaning_24h(job_id):
    """Process 24-hour cleaning start"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)
        
        # Get duration from form
        duration_option = request.form.get('duration_option', '24')
        if duration_option == 'custom':
            duration_hours = float(request.form.get('custom_hours', 24))
        else:
            duration_hours = float(duration_option)
        
        # Create cleaning process
        cleaning_process = CleaningProcess()
        cleaning_process.job_id = job_id
        cleaning_process.process_type = f'{int(duration_hours)}_hour' if duration_hours == int(duration_hours) else 'custom'
        cleaning_process.duration_hours = duration_hours
        cleaning_process.start_time = datetime.now()
        cleaning_process.end_time = datetime.now() + timedelta(hours=duration_hours)
        cleaning_process.start_moisture = float(request.form.get('initial_moisture', 0)) if request.form.get('initial_moisture') else None
        cleaning_process.operator_name = request.form['operator_name']
        cleaning_process.machine_name = request.form.get('machine_name', 'Cleaning Machine')
        cleaning_process.status = 'running'
        
        # Handle cleaning bin assignment if provided
        if request.form.get('cleaning_bin_id'):
            cleaning_process.cleaning_bin_id = int(request.form['cleaning_bin_id'])
            # Update bin status
            cleaning_bin = CleaningBin.query.get(cleaning_process.cleaning_bin_id)
            if cleaning_bin:
                cleaning_bin.status = 'cleaning'
        
        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.now()
        job.started_by = request.form['operator_name']
        
        db.session.add(cleaning_process)
        db.session.commit()
        
        flash(f'{duration_hours}-hour cleaning process started successfully!', 'success')
        return redirect(url_for('production_execution'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error starting cleaning process: {str(e)}', 'error')
        return redirect(url_for('cleaning_setup', job_id=job_id))

@app.route('/debug_production_order')
def debug_production_order():
    """Debug route to test production order creation"""
    try:
        from sqlalchemy import text
        
        # Test database connection
        result = db.session.execute(text("SELECT 1")).fetchone()
        print("Database connection: OK")
        
        # Check production_order table structure
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'production_order'
            ORDER BY column_name;
        """)).fetchall()
        
        print("Production Order table structure:")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
        
        # Test creating a simple production order
        test_order = ProductionOrder(
            order_number=generate_order_number('TEST'),
            quantity=100.0,
            product='Test Product',
            created_by='Debug Test'
        )
        
        db.session.add(test_order)
        db.session.commit()
        
        return f"Debug successful! Test order created with ID: {test_order.id}"
        
    except Exception as e:
        db.session.rollback()
        return f"Debug error: {str(e)}"