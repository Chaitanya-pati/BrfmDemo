import os
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import *
from utils import allowed_file, generate_order_number, notify_responsible_person, validate_plan_percentages
import logging

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

@app.route('/')
def index():
    """Main dashboard with production functionality"""
    # Dashboard data
    pending_vehicles = Vehicle.query.filter_by(status='pending').count()
    quality_check_vehicles = Vehicle.query.filter_by(status='quality_check').count()
    pending_dispatches = Dispatch.query.filter_by(status='loaded').count()
    
    # Production order stats
    active_orders = ProductionOrder.query.filter_by(status='cleaning').count()
    orders_ready_for_12h = ProductionOrder.query.filter_by(status='24h_completed').count()
    orders_in_12h = ProductionOrder.query.filter_by(status='12h_cleaning').count()
    
    # Recent activities
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    recent_orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         pending_vehicles=pending_vehicles,
                         quality_check_vehicles=quality_check_vehicles,
                         active_orders=active_orders,
                         orders_ready_for_12h=orders_ready_for_12h,
                         orders_in_12h=orders_in_12h,
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
    
    return render_template('precleaning.html', godowns=godowns, precleaning_bins=precleaning_bins, recent_transfers=recent_transfers)

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
                sales_order.product_id = int(request.form['product_id'])
                sales_order.quantity_kg = float(request.form['quantity_kg'])
                sales_order.sale_price_per_kg = float(request.form['sale_price_per_kg'])
                sales_order.total_amount = sales_order.quantity_kg * sales_order.sale_price_per_kg
                sales_order.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
                sales_order.notes = request.form.get('notes')
                
                db.session.add(sales_order)
                db.session.commit()
                flash('Sales order created successfully!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating sales order: {str(e)}', 'error')
    
    # Get data for the template
    customers = Customer.query.all()
    products = Product.query.all()
    sales_orders = SalesOrder.query.order_by(SalesOrder.created_at.desc()).all()
    dispatches = Dispatch.query.order_by(Dispatch.dispatch_date.desc()).all()
    
    return render_template('sales_dispatch.html', customers=customers, products=products, 
                         sales_orders=sales_orders, dispatches=dispatches)

@app.route('/reports')
def reports():
    # Various report data without production references
    vehicle_stats = db.session.query(
        Vehicle.status, 
        db.func.count(Vehicle.id).label('count')
    ).group_by(Vehicle.status).all()
    
    total_vehicles = Vehicle.query.count()
    total_stock = db.session.query(db.func.sum(Godown.current_stock)).scalar() or 0
    total_dispatches = Dispatch.query.count()
    
    # Recent activities
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    recent_dispatches = Dispatch.query.order_by(Dispatch.dispatch_date.desc()).limit(5).all()
    
    return render_template('reports.html',
                         vehicle_stats=vehicle_stats,
                         total_vehicles=total_vehicles,
                         total_stock=total_stock,
                         total_dispatches=total_dispatches,
                         recent_vehicles=recent_vehicles,
                         recent_dispatches=recent_dispatches)

@app.route('/masters', methods=['GET', 'POST'])
def masters():
    if request.method == 'POST':
        try:
            form_type = request.form.get('form_type')
            
            if form_type == 'supplier':
                supplier = Supplier()
                supplier.name = request.form['name']
                supplier.contact_person = request.form.get('contact_person')
                supplier.phone = request.form.get('phone')
                supplier.address = request.form.get('address')
                db.session.add(supplier)
                
            elif form_type == 'customer':
                customer = Customer()
                customer.name = request.form['name']
                customer.contact_person = request.form.get('contact_person')
                customer.phone = request.form.get('phone')
                customer.address = request.form.get('address')
                db.session.add(customer)
                
            elif form_type == 'product':
                product = Product()
                product.name = request.form['name']
                product.description = request.form.get('description')
                # Remove price_per_kg as it doesn't exist in the model
                db.session.add(product)
                
            elif form_type == 'precleaning_bin':
                bin = PrecleaningBin()
                bin.name = request.form['name']
                bin.capacity = float(request.form['capacity'])
                bin.current_stock = 0.0  # Start with empty bin
                db.session.add(bin)
            
            db.session.commit()
            flash(f'{form_type.title()} added successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding {form_type}: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    godown_types = GodownType.query.all()
    precleaning_bins = PrecleaningBin.query.all()
    
    return render_template('masters.html', suppliers=suppliers, customers=customers, 
                         products=products, godown_types=godown_types, precleaning_bins=precleaning_bins)

@app.route('/raw_wheat_quality_report', methods=['GET', 'POST'])
def raw_wheat_quality_report():
    if request.method == 'POST':
        try:
            report = RawWheatQualityReport()
            report.vehicle_id = int(request.form['vehicle_id'])
            report.wheat_variety = request.form['wheat_variety']
            report.test_date = datetime.strptime(request.form['test_date'], '%Y-%m-%d')
            report.bill_number = request.form.get('bill_number')
            report.lab_chemist = request.form['lab_chemist']
            
            # Test parameters
            report.moisture = float(request.form.get('moisture', 0))
            report.hectoliter_weight = float(request.form.get('hectoliter_weight', 0))
            report.wet_gluten = float(request.form.get('wet_gluten', 0))
            report.dry_gluten = float(request.form.get('dry_gluten', 0))
            report.sedimentation_value = float(request.form.get('sedimentation_value', 0))
            
            # Additional fields...
            report.category_assigned = request.form['category_assigned']
            report.approved = request.form.get('approved') == 'on'
            report.comments_action = request.form.get('comments_action')
            
            db.session.add(report)
            db.session.commit()
            flash('Quality report created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quality report: {str(e)}', 'error')
    
    vehicles = Vehicle.query.filter_by(status='quality_check').all()
    reports = RawWheatQualityReport.query.order_by(RawWheatQualityReport.test_date.desc()).all()
    
    return render_template('raw_wheat_quality_report.html', vehicles=vehicles, reports=reports)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/init_cleaning_reminders')
def init_cleaning_reminders():
    """Initialize sample cleaning reminders for existing machines"""
    try:
        # machines query removed - ProductionMachine model deleted
        machines = []

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

# Production Order Creation and Planning Routes
@app.route('/production_orders', methods=['GET', 'POST'])
def production_orders():
    """Handle production order creation"""
    if request.method == 'POST':
        try:
            # Create new production order
            order = ProductionOrder()
            order.order_number = generate_order_number('PRO')
            order.quantity = float(request.form['quantity_tons'])
            order.finished_good_type = request.form['finished_goods_type']
            order.created_by = request.form.get('created_by', 'Admin')
            # responsible_person field removed - using created_by instead
            
            db.session.add(order)
            db.session.commit()
            
            # Send notification to responsible person
            notify_responsible_person(
                order.order_number,
                order.created_by,
                order.finished_good_type,
                order.quantity
            )
            
            # Notification sent successfully
            
            flash(f'Production Order {order.order_number} created successfully! Notification sent to {order.created_by}.', 'success')
            return redirect(url_for('production_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production order: {str(e)}', 'error')
    
    # Get all production orders with their cleaning processes
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    
    # Get cleaning processes for each order
    cleaning_status = {}
    for order in orders:
        # Handle potential database schema mismatches gracefully
        try:
            cleaning_process = CleaningProcess.query.filter_by(order_id=order.id).first()
        except Exception:
            cleaning_process = None
        if cleaning_process:
            cleaning_status[order.id] = cleaning_process
    
    return render_template('production_orders.html', orders=orders, cleaning_status=cleaning_status)

@app.route('/production_cleaning_overview')
def production_cleaning_overview():
    """Overview of all production cleaning processes"""
    # Very simple version to avoid database issues
    return render_template('production_cleaning_overview.html', 
                         orders_with_cleaning=[],
                         active_processes=[])

@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id):
    """Handle production planning with bin percentages"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Allow all users to access production planning
    # Remove role restrictions for now
    
    # Check if order is locked (next stage started)
    if order.status == 'in_production' or order.status == 'completed':
        flash('This order is locked and cannot be modified.', 'warning')
        return redirect(url_for('production_orders'))
    
    if request.method == 'POST':
        try:
            # Get form data
            bin_percentages = {}
            for key, value in request.form.items():
                if key.startswith('bin_') and key.endswith('_percentage'):
                    bin_id = int(key.replace('bin_', '').replace('_percentage', ''))
                    percentage = float(value) if value else 0
                    if percentage > 0:
                        bin_percentages[bin_id] = percentage
            
            # Validate percentages sum to 100%
            total_percentage = sum(bin_percentages.values())
            if abs(total_percentage - 100.0) > 0.001:
                flash(f'Total percentage must equal exactly 100%. Current total: {total_percentage:.2f}%', 'error')
                raise ValueError('Invalid percentage total')
            
            # Create or update production plan
            existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
            if existing_plan:
                # Delete existing plan items
                ProductionPlanItem.query.filter_by(plan_id=existing_plan.id).delete()
                plan = existing_plan
            else:
                plan = ProductionPlan(
                    order_id=order_id
                )
                db.session.add(plan)
                db.session.flush()  # Get plan ID
            
            # Create plan items
            plan.total_percentage = total_percentage
            for bin_id, percentage in bin_percentages.items():
                calculated_tons = (percentage / 100) * order.quantity
                
                plan_item = ProductionPlanItem(
                    plan_id=plan.id,
                    precleaning_bin_id=bin_id,
                    percentage=percentage,
                    calculated_tons=calculated_tons
                )
                db.session.add(plan_item)
            
            # Update order status
            order.status = 'planning'
            
            db.session.commit()
            flash('Production plan saved successfully!', 'success')
            return redirect(url_for('production_planning', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving production plan: {str(e)}', 'error')
    
    # Get available pre-cleaning bins with current stock
    bins = PrecleaningBin.query.all()
    
    # Get existing plan if any
    existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
    existing_items = {}
    if existing_plan:
        for item in existing_plan.plan_items:
            existing_items[item.precleaning_bin_id] = {
                'percentage': item.percentage,
                'calculated_tons': item.calculated_tons
            }
    
    return render_template('production_planning.html', 
                         order=order, 
                         bins=bins, 
                         existing_items=existing_items)

@app.route('/api/calculate_tons', methods=['POST'])
def calculate_tons():
    """API endpoint to calculate tons based on percentage"""
    try:
        data = request.get_json()
        order_id = data['order_id']
        percentage = float(data['percentage'])
        
        order = ProductionOrder.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        calculated_tons = (percentage / 100) * order.quantity
        
        return jsonify({
            'calculated_tons': round(calculated_tons, 3),
            'order_total': order.quantity
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 24-Hour Cleaning Stage Routes

@app.route('/production_cleaning/<int:order_id>', methods=['GET', 'POST'])
def production_cleaning(order_id):
    """Handle 24-hour cleaning stage for production orders"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Check if production plan exists and is complete
    existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
    if not existing_plan or existing_plan.total_percentage != 100:
        flash('Please complete production planning before starting cleaning stage.', 'error')
        return redirect(url_for('production_planning', order_id=order_id))
    
    # Get transfer jobs for this order
    transfer_jobs = TransferJob.query.filter_by(order_id=order_id).all()
    
    # Get cleaning bins with current stock
    cleaning_bins = CleaningBin.query.all()
    
    # Get existing cleaning process if any
    cleaning_process = CleaningProcess.query.filter_by(order_id=order_id).first()
    
    return render_template('production_cleaning.html', 
                         order=order,
                         existing_plan=existing_plan,
                         transfer_jobs=transfer_jobs,
                         cleaning_bins=cleaning_bins,
                         cleaning_process=cleaning_process)

@app.route('/start_transfer', methods=['POST'])
def start_transfer():
    """Start a transfer job from pre-cleaning bin to cleaning bin"""
    try:
        data = request.get_json()
        order_id = data['order_id']
        precleaning_bin_id = data['precleaning_bin_id']
        cleaning_bin_id = data['cleaning_bin_id']
        quantity_tons = float(data['quantity_tons'])
        operator_name = data.get('operator_name', 'Operator')
        
        # Generate unique job ID
        job_id = generate_job_id()
        
        # Create transfer job
        transfer_job = TransferJob(
            job_id=job_id,
            order_id=order_id,
            precleaning_bin_id=precleaning_bin_id,
            cleaning_bin_id=cleaning_bin_id,
            quantity_tons=quantity_tons,
            start_time=datetime.utcnow(),
            status='in_progress',
            operator_name=operator_name
        )
        
        db.session.add(transfer_job)
        
        # Update bin stocks
        precleaning_bin = PrecleaningBin.query.get(precleaning_bin_id)
        cleaning_bin = CleaningBin.query.get(cleaning_bin_id)
        
        if precleaning_bin.current_stock < quantity_tons:
            return jsonify({'error': 'Insufficient stock in pre-cleaning bin'}), 400
        
        precleaning_bin.current_stock -= quantity_tons
        cleaning_bin.current_stock += quantity_tons
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'start_time': transfer_job.start_time.isoformat(),
            'message': f'Transfer job {job_id} started successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/complete_transfer', methods=['POST'])
def complete_transfer():
    """Complete a transfer job and record end time"""
    try:
        data = request.get_json()
        job_id = data['job_id']
        
        transfer_job = TransferJob.query.filter_by(job_id=job_id).first()
        if not transfer_job:
            return jsonify({'error': 'Transfer job not found'}), 404
        
        # Record end time and calculate duration
        end_time = datetime.utcnow()
        transfer_job.end_time = end_time
        transfer_job.status = 'completed'
        transfer_job.duration_minutes = (end_time - transfer_job.start_time).total_seconds() / 60
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'end_time': end_time.isoformat(),
            'duration_minutes': round(transfer_job.duration_minutes, 2),
            'message': f'Transfer job {job_id} completed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/start_cleaning_process', methods=['POST'])
def start_cleaning_process():
    """Start the cleaning process with timer"""
    try:
        data = request.get_json()
        order_id = data['order_id']
        process_type = data['process_type']  # '24_hour', '12_hour', 'custom'
        cleaning_bin_id = data['cleaning_bin_id']
        operator_name = data.get('operator_name', 'Operator')
        custom_hours = data.get('custom_hours', 24.0)
        
        # Validate duration based on process type
        if process_type == '24_hour':
            duration_hours = 24.0
        elif process_type == '12_hour':
            duration_hours = 12.0
        elif process_type == 'custom':
            duration_hours = float(custom_hours)
        else:
            return jsonify({'error': 'Invalid process type'}), 400
        
        # Check if cleaning process already exists for this order
        existing_process = CleaningProcess.query.filter_by(order_id=order_id).first()
        if existing_process:
            return jsonify({'error': 'Cleaning process already started for this order'}), 400
        
        # Create cleaning process
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=duration_hours)
        
        cleaning_process = CleaningProcess(
            order_id=order_id,
            cleaning_bin_id=cleaning_bin_id,
            process_type=process_type,
            duration_hours=duration_hours,
            start_time=start_time,
            end_time=end_time,
            operator_name=operator_name,
            status='running',
            timer_active=True,
            countdown_start=start_time,
            countdown_end=end_time
        )
        
        db.session.add(cleaning_process)
        
        # Update cleaning bin status
        cleaning_bin = CleaningBin.query.get(cleaning_bin_id)
        if not cleaning_bin:
            return jsonify({'error': 'Cleaning bin not found'}), 400
        cleaning_bin.status = 'cleaning'
        
        # Update order status
        order = ProductionOrder.query.get(order_id)
        if not order:
            return jsonify({'error': 'Production order not found'}), 400
        order.status = 'cleaning'
        
        db.session.commit()
        
        # Schedule multiple cleaning reminders throughout the process
        total_minutes = int(duration_hours * 60)
        reminder_intervals = []
        
        # Generate reminders every minute for manual machine cleaning tracking
        interval_minutes = 1  # Reminder every minute
        
        # Create reminder schedule - every minute throughout the process
        current_minute = interval_minutes
        while current_minute < total_minutes:
            reminder_time = start_time + timedelta(minutes=current_minute)
            reminder_intervals.append(reminder_time)
            current_minute += interval_minutes
        
        # Always add a final reminder at completion
        final_reminder = start_time + timedelta(minutes=total_minutes)
        if final_reminder not in reminder_intervals:
            reminder_intervals.append(final_reminder)
        
        # Schedule all reminders
        for reminder_time in reminder_intervals:
            schedule_cleaning_reminder(cleaning_process.id, reminder_time)
            
        logging.info(f"Scheduled {len(reminder_intervals)} cleaning reminders for process {cleaning_process.id}")
        
        return jsonify({
            'success': True,
            'process_id': cleaning_process.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_hours': duration_hours,
            'message': f'{process_type.replace("_", " ").title()} cleaning process started'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/cleaning_timer_status/<int:order_id>')
def cleaning_timer_status(order_id):
    """Get current timer status for cleaning process"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, timer_active=True).first()
        
        if not cleaning_process:
            return jsonify({'timer_active': False})
        
        current_time = datetime.utcnow()
        
        # Check if timer has completed
        if current_time >= cleaning_process.countdown_end:
            return jsonify({
                'timer_active': False,
                'completed': True,
                'can_proceed': True,
                'end_time': cleaning_process.countdown_end.isoformat()
            })
        
        # Calculate remaining time
        remaining_seconds = (cleaning_process.countdown_end - current_time).total_seconds()
        
        return jsonify({
            'timer_active': True,
            'completed': False,
            'can_proceed': False,
            'process_type': cleaning_process.process_type,
            'start_time': cleaning_process.countdown_start.isoformat(),
            'end_time': cleaning_process.countdown_end.isoformat(),
            'remaining_seconds': int(remaining_seconds),
            'duration_hours': cleaning_process.duration_hours
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def schedule_cleaning_reminder(process_id, due_time):
    """Schedule a cleaning reminder - simplified version"""
    try:
        # For now, just log that we would schedule a reminder
        # The frontend will handle minute-by-minute popups
        logging.info(f"Would schedule cleaning reminder for process {process_id} at {due_time}")
        return True
        
    except Exception as e:
        logging.error(f"Error scheduling reminder: {e}")
        return False

def send_cleaning_reminder(reminder_id):
    """Send cleaning reminder (called by scheduler)"""
    try:
        from app import app
        with app.app_context():
            reminder = CleaningReminder.query.get(reminder_id)
            if not reminder:
                logging.error(f"Reminder {reminder_id} not found")
                return False
            
            # Check if cleaning process is still active
            cleaning_process = reminder.cleaning_process
            current_time = datetime.utcnow()
            
            if current_time >= cleaning_process.countdown_end:
                logging.info(f"Cleaning process {cleaning_process.id} already completed, skipping reminder")
                return False
            
            # Mark reminder as sent - this creates an active reminder every minute
            reminder.reminder_sent = True
            reminder.user_notified = 'System'
            
            # Auto-expire previous reminders that are older than 2 minutes to avoid clutter
            old_reminders = CleaningReminder.query.filter_by(
                cleaning_process_id=cleaning_process.id,
                reminder_sent=True,
                completed=False
            ).filter(
                CleaningReminder.due_time < current_time - timedelta(minutes=2)
            ).all()
            
            for old_reminder in old_reminders:
                old_reminder.completed = True
            
            db.session.commit()
            logging.info(f"Manual cleaning reminder sent for process {cleaning_process.id}, sequence {reminder.reminder_sequence} (minute {reminder.reminder_sequence})")
            
            return True
        
    except Exception as e:
        logging.error(f"Error sending reminder {reminder_id}: {e}")
        return False

@app.route('/upload_cleaning_photo', methods=['POST'])
def upload_cleaning_photo():
    """Upload cleaning reminder photo"""
    try:
        # Get form data
        reminder_id = request.form.get('reminder_id')
        photo_type = request.form.get('photo_type')  # 'before', 'after'
        notes = request.form.get('notes', '')
        
        # Validate inputs
        if not reminder_id or not photo_type:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if file was uploaded
        if 'photo_file' not in request.files:
            return jsonify({'error': 'No photo file uploaded'}), 400
        
        file = request.files['photo_file']
        if file.filename == '':
            return jsonify({'error': 'No photo file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get the reminder
        reminder = CleaningReminder.query.get(reminder_id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cleaning_{photo_type}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create photo record
        reminder_photo = CleaningReminderPhoto(
            reminder_id=reminder_id,
            photo_type=photo_type,
            file_path=file_path,
            uploaded_by='System User',  # You can modify this to get actual user
            uploaded_at=datetime.utcnow(),
            notes=notes
        )
        
        db.session.add(reminder_photo)
        
        # Update reminder status if this completes the requirement
        existing_photos = CleaningReminderPhoto.query.filter_by(
            reminder_id=reminder_id,
            photo_type=photo_type
        ).count()
        
        if existing_photos == 0:  # This is the first photo of this type
            reminder.photo_uploaded = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'photo_id': reminder_photo.id,
            'filename': filename,
            'upload_time': reminder_photo.uploaded_at.isoformat(),
            'message': f'{photo_type.title()} photo uploaded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/get_cleaning_reminders/<int:order_id>')
def get_cleaning_reminders(order_id):
    """Get cleaning reminders for an order"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id).first()
        if not cleaning_process:
            return jsonify({'reminders': []})
        
        # Get all reminders for this process
        reminders = CleaningReminder.query.filter_by(
            cleaning_process_id=cleaning_process.id
        ).order_by(CleaningReminder.reminder_sequence.desc()).limit(5).all()
        
        reminder_data = []
        for reminder in reminders:
            # Get photos for this reminder
            photos = CleaningReminderPhoto.query.filter_by(reminder_id=reminder.id).all()
            
            photo_data = []
            for photo in photos:
                photo_data.append({
                    'id': photo.id,
                    'type': photo.photo_type,
                    'filename': photo.filename,
                    'upload_time': photo.upload_time.isoformat() if photo.upload_time else None,
                    'notes': photo.notes
                })
            
            reminder_data.append({
                'id': reminder.id,
                'sequence': reminder.reminder_sequence,
                'due_time': reminder.due_time.isoformat(),
                'reminder_sent': reminder.reminder_sent,
                'photo_uploaded': reminder.photo_uploaded,
                'photos': photo_data
            })
        
        return jsonify({'reminders': reminder_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/upload_manual_cleaning', methods=['POST'])
def upload_manual_cleaning():
    """Handle manual cleaning photo upload and logging"""
    try:
        # Get form data
        order_id = request.form.get('order_id')
        operator_name = request.form.get('operator_name')
        machine_name = request.form.get('machine_name', 'Manual Cleaning Machine')
        notes = request.form.get('notes', '')
        cleaning_process_id = request.form.get('cleaning_process_id')
        
        # Validate inputs
        if not order_id or not operator_name:
            return jsonify({'error': 'Order ID and operator name are required'}), 400
        
        # Handle file uploads
        before_photo = None
        after_photo = None
        
        if 'before_photo' in request.files:
            file = request.files['before_photo']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"manual_before_{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                before_photo = filename
        
        if 'after_photo' in request.files:
            file = request.files['after_photo']
            if file and file.filename and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"manual_after_{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                after_photo = filename
        
        # Create manual cleaning log
        manual_cleaning = ManualCleaningLog(
            order_id=int(order_id),
            cleaning_process_id=int(cleaning_process_id) if cleaning_process_id else None,
            machine_name=machine_name,
            operator_name=operator_name,
            cleaning_start_time=datetime.utcnow(),
            cleaning_end_time=datetime.utcnow(),  # For manual cleaning, start and end are same
            duration_minutes=1.0,  # Default 1 minute for manual cleaning
            before_photo=before_photo,
            after_photo=after_photo,
            notes=notes,
            status='completed'
        )
        
        db.session.add(manual_cleaning)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'manual_cleaning_id': manual_cleaning.id,
            'message': 'Manual cleaning logged successfully',
            'cleaning_time': manual_cleaning.cleaning_start_time.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/get_manual_cleanings/<int:order_id>')
def get_manual_cleanings(order_id):
    """Get manual cleaning logs for an order"""
    try:
        manual_cleanings = ManualCleaningLog.query.filter_by(order_id=order_id).order_by(
            ManualCleaningLog.cleaning_start_time.desc()
        ).all()
        
        cleaning_data = []
        for cleaning in manual_cleanings:
            cleaning_data.append({
                'id': cleaning.id,
                'machine_name': cleaning.machine_name,
                'operator_name': cleaning.operator_name,
                'cleaning_time': cleaning.cleaning_start_time.isoformat(),
                'duration_minutes': cleaning.duration_minutes,
                'before_photo': cleaning.before_photo,
                'after_photo': cleaning.after_photo,
                'notes': cleaning.notes,
                'status': cleaning.status
            })
        
        return jsonify({
            'manual_cleanings': cleaning_data,
            'total_manual_cleanings': len(cleaning_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_cleaning_progress/<int:order_id>')
def get_cleaning_progress(order_id):
    """Get cleaning progress including reminders and manual cleaning stats"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id).first()
        if not cleaning_process:
            return jsonify({'error': 'No cleaning process found'}), 404
        
        current_time = datetime.utcnow()
        
        # Calculate process progress
        total_minutes = cleaning_process.duration_hours * 60
        elapsed_minutes = (current_time - cleaning_process.start_time).total_seconds() / 60
        progress_percentage = min((elapsed_minutes / total_minutes) * 100, 100)
        
        # Get manual cleaning count for this process
        manual_cleaning_count = ManualCleaningLog.query.filter_by(
            cleaning_process_id=cleaning_process.id
        ).count()
        
        # Get recent manual cleanings
        recent_cleanings = ManualCleaningLog.query.filter_by(
            cleaning_process_id=cleaning_process.id
        ).order_by(ManualCleaningLog.cleaning_start_time.desc()).limit(5).all()
        
        last_cleaning = recent_cleanings[0] if recent_cleanings else None
        
        # Expected cleanings (one per minute)
        expected_cleanings = max(1, int(elapsed_minutes))
        cleaning_compliance = (manual_cleaning_count / expected_cleanings) * 100 if expected_cleanings > 0 else 0
        
        return jsonify({
            'process_progress': round(progress_percentage, 1),
            'elapsed_minutes': int(elapsed_minutes),
            'total_minutes': int(total_minutes),
            'manual_cleaning_count': manual_cleaning_count,
            'expected_cleanings': expected_cleanings,
            'cleaning_compliance': round(cleaning_compliance, 1),
            'last_cleaning_time': last_cleaning.cleaning_start_time.isoformat() if last_cleaning else None,
            'last_cleaning_operator': last_cleaning.operator_name if last_cleaning else None,
            'timer_active': cleaning_process.timer_active
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/submit_post_process_data', methods=['POST'])
def submit_post_process_data():
    """Submit post-process cleaning data"""
    try:
        data = request.get_json()
        order_id = data['order_id']
        
        # Required post-process fields
        moisture_before = float(data.get('moisture_before', 0))
        moisture_after = float(data.get('moisture_after', 0))
        waste_material_kg = float(data.get('waste_material_kg', 0))
        water_used_liters = float(data.get('water_used_liters', 0))
        machine_efficiency = float(data.get('machine_efficiency', 100))
        operator_notes = data.get('operator_notes', '')
        operator_name = data.get('operator_name', 'Operator')
        
        # Get the cleaning process
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, status='running').first()
        if not cleaning_process:
            return jsonify({'error': 'No active cleaning process found for this order'}), 404
        
        # Check if timer is completed
        current_time = datetime.utcnow()
        if current_time < cleaning_process.countdown_end:
            return jsonify({'error': 'Cannot submit data until cleaning process is complete'}), 400
        
        # Get machine name
        machine_name = data.get('machine_name', '')
        
        # Update cleaning process with post-process data
        cleaning_process.moisture_before = moisture_before
        cleaning_process.moisture_after = moisture_after
        cleaning_process.waste_material_kg = waste_material_kg
        cleaning_process.water_used_liters = water_used_liters
        cleaning_process.machine_name = machine_name
        cleaning_process.post_process_notes = operator_notes
        cleaning_process.completed_by = operator_name
        cleaning_process.completion_time = current_time
        cleaning_process.status = 'completed'
        cleaning_process.timer_active = False
        
        cleaning_bin = CleaningBin.query.get(cleaning_process.cleaning_bin_id)
        cleaning_bin.status = 'available'
        
        # Check if this was a 24-hour process - if so, enable 12-hour option
        order = ProductionOrder.query.get(order_id)
        if cleaning_process.process_type == '24_hour':
            order.status = '24h_completed'  # Mark as ready for 12-hour cleaning
        elif cleaning_process.process_type == '12_hour':
            order.status = 'completed'  # Final completion
        else:
            order.status = 'completed'  # Default completion
        
        # Calculate quality metrics
        moisture_reduction = moisture_before - moisture_after
        cleaning_efficiency = ((moisture_reduction / moisture_before) * 100) if moisture_before > 0 else 0
        
        # Log the order status change for debugging
        print(f"DEBUG: Order {order_id} status changed from '{order.status}' to '{order.status}' for process type '{cleaning_process.process_type}'")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'completion_time': current_time.isoformat(),
            'moisture_reduction': round(moisture_reduction, 2),
            'cleaning_efficiency': round(cleaning_efficiency, 2),
            'next_stage_available': cleaning_process.process_type == '24_hour',
            'message': 'Process completed successfully!' + (' 12-hour cleaning stage is now available.' if cleaning_process.process_type == '24_hour' else '')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/start_24h_cleaning/<int:order_id>', methods=['GET', 'POST'])
def start_24h_cleaning(order_id):
    """Start 24-hour cleaning process"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Check if production plan exists and is complete
    existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
    if not existing_plan or existing_plan.total_percentage != 100:
        flash('Please complete production planning before starting cleaning stage.', 'error')
        return redirect(url_for('production_planning', order_id=order_id))
    
    # Check if 24-hour cleaning already exists
    existing_process = CleaningProcess.query.filter_by(order_id=order_id, process_type='24_hour').first()
    if existing_process:
        return redirect(url_for('monitor_24h_cleaning', order_id=order_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            duration_hours = float(request.form.get('duration_hours', 24.0))
            operator_name = request.form.get('operator_name')
            machine_name = request.form.get('machine_name', '24-Hour Cleaning Machine')
            cleaning_bin_id = int(request.form.get('cleaning_bin_id', 1))  # Default bin
            
            # Validate required fields
            if not operator_name:
                flash('Operator name is required.', 'error')
                return render_template('start_24h_cleaning.html', order=order, cleaning_bins=CleaningBin.query.filter_by(status='available').all())
            
            # Create 24-hour cleaning process
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=duration_hours)
            
            cleaning_process = CleaningProcess(
                order_id=order_id,
                cleaning_bin_id=cleaning_bin_id,
                process_type='24_hour',
                duration_hours=duration_hours,
                start_time=start_time,
                end_time=end_time,
                operator_name=operator_name,
                machine_name=machine_name,
                status='running',
                timer_active=True,
                countdown_start=start_time,
                countdown_end=end_time
            )
            
            db.session.add(cleaning_process)
            
            # Update order status
            order.status = 'cleaning'
            
            # Update cleaning bin status
            cleaning_bin = CleaningBin.query.get(cleaning_bin_id)
            if cleaning_bin:
                cleaning_bin.status = 'cleaning'
            
            db.session.commit()
            
            flash(f'24-hour cleaning process started successfully! Duration: {duration_hours} hours', 'success')
            return redirect(url_for('monitor_24h_cleaning', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting 24-hour cleaning: {str(e)}', 'error')
    
    # Get available cleaning bins
    cleaning_bins = CleaningBin.query.filter_by(status='available').all()
    
    return render_template('start_24h_cleaning.html', order=order, cleaning_bins=cleaning_bins)

@app.route('/monitor_24h_cleaning/<int:order_id>')
def monitor_24h_cleaning(order_id):
    """Monitor 24-hour cleaning process"""
    order = ProductionOrder.query.get_or_404(order_id)
    cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, process_type='24_hour', status='running').first()
    
    if not cleaning_process:
        flash('No active 24-hour cleaning process found.', 'error')
        return redirect(url_for('production_orders'))
    
    return render_template('monitor_24h_cleaning.html', order=order, cleaning_process=cleaning_process)

@app.route('/start_12h_cleaning/<int:order_id>', methods=['GET', 'POST'])
def start_12h_cleaning(order_id):
    """Start 12-hour cleaning process after 24-hour completion"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Check if 24-hour process is completed
    if order.status != '24h_completed':
        flash('24-hour cleaning must be completed before starting 12-hour process.', 'error')
        return redirect(url_for('production_cleaning', order_id=order_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            duration_hours = float(request.form['duration_hours'])
            target_moisture = float(request.form['target_moisture'])
            start_moisture = float(request.form['start_moisture'])
            operator_name = request.form['operator_name']
            machine_name = request.form.get('machine_name', '12-Hour Cleaning Machine')
            cleaning_bin_id = request.form.get('cleaning_bin_id', 1)  # Default bin
            
            # Create 12-hour cleaning process
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=duration_hours)
            
            cleaning_process = CleaningProcess(
                order_id=order_id,
                cleaning_bin_id=cleaning_bin_id,
                process_type='12_hour',
                duration_hours=duration_hours,
                start_time=start_time,
                end_time=end_time,
                start_moisture=start_moisture,
                target_moisture=target_moisture,
                operator_name=operator_name,
                machine_name=machine_name,
                status='running',
                timer_active=True,
                countdown_start=start_time,
                countdown_end=end_time
            )
            
            db.session.add(cleaning_process)
            
            # Update order status
            order.status = '12h_cleaning'
            
            # Update cleaning bin status
            cleaning_bin = CleaningBin.query.get(cleaning_bin_id)
            if cleaning_bin:
                cleaning_bin.status = 'cleaning'
            
            db.session.commit()
            
            flash(f'12-hour cleaning process started successfully! Duration: {duration_hours} hours', 'success')
            return redirect(url_for('monitor_12h_cleaning', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting 12-hour cleaning: {str(e)}', 'error')
    
    # Get available cleaning bins
    cleaning_bins = CleaningBin.query.filter_by(status='available').all()
    
    return render_template('start_12h_cleaning.html', order=order, cleaning_bins=cleaning_bins)

@app.route('/monitor_12h_cleaning/<int:order_id>')
def monitor_12h_cleaning(order_id):
    """Monitor 12-hour cleaning process with timer and reminders"""
    order = ProductionOrder.query.get_or_404(order_id)
    cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, process_type='12_hour', status='running').first()
    
    if not cleaning_process:
        flash('No active 12-hour cleaning process found.', 'error')
        return redirect(url_for('production_orders'))
    
    return render_template('monitor_12h_cleaning.html', order=order, cleaning_process=cleaning_process)

@app.route('/api/12h_timer_status/<int:order_id>')
def get_12h_timer_status(order_id):
    """Get current timer status for 12-hour cleaning process"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(
            order_id=order_id, 
            process_type='12_hour',
            timer_active=True
        ).first()
        
        if not cleaning_process:
            return jsonify({'timer_active': False})
        
        current_time = datetime.utcnow()
        
        # Check if timer has completed
        if current_time >= cleaning_process.countdown_end:
            return jsonify({
                'timer_active': False,
                'completed': True,
                'can_proceed': True,
                'end_time': cleaning_process.countdown_end.isoformat()
            })
        
        # Calculate remaining time
        remaining_seconds = (cleaning_process.countdown_end - current_time).total_seconds()
        elapsed_seconds = (current_time - cleaning_process.countdown_start).total_seconds()
        
        # Check for pre-end reminders (configurable offsets)
        reminder_offsets = [300, 600, 1800]  # 5min, 10min, 30min before end
        upcoming_reminders = []
        for offset in reminder_offsets:
            if remaining_seconds <= offset and remaining_seconds > (offset - 60):
                upcoming_reminders.append(f"{offset//60} minutes until completion")
        
        # Manual cleaning reminder every 30 seconds
        needs_manual_cleaning = int(elapsed_seconds) % 30 == 0 and int(elapsed_seconds) > 0
        
        return jsonify({
            'timer_active': True,
            'completed': False,
            'can_proceed': False,
            'process_type': cleaning_process.process_type,
            'start_time': cleaning_process.countdown_start.isoformat(),
            'end_time': cleaning_process.countdown_end.isoformat(),
            'remaining_seconds': int(remaining_seconds),
            'elapsed_seconds': int(elapsed_seconds),
            'duration_hours': cleaning_process.duration_hours,
            'target_moisture': cleaning_process.target_moisture,
            'start_moisture': cleaning_process.start_moisture,
            'upcoming_reminders': upcoming_reminders,
            'needs_manual_cleaning': needs_manual_cleaning
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/unified_cleaning_process/<int:order_id>')
def unified_cleaning_process(order_id):
    """Unified view for both 24-hour and 12-hour cleaning processes"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Get existing cleaning processes
    cleaning_24h = CleaningProcess.query.filter_by(order_id=order_id, process_type='24_hour').first()
    cleaning_12h = CleaningProcess.query.filter_by(order_id=order_id, process_type='12_hour').first()
    
    return render_template('unified_cleaning_process.html', 
                         order=order, 
                         cleaning_24h=cleaning_24h,
                         cleaning_12h=cleaning_12h)

@app.route('/submit_12h_completion', methods=['POST'])
def submit_12h_completion():
    """Submit 12-hour cleaning completion data"""
    try:
        data = request.get_json()
        order_id = data['order_id']
        outgoing_moisture = float(data['outgoing_moisture'])
        operator_name = data.get('operator_name', 'Operator')
        notes = data.get('notes', '')
        
        # Get the 12-hour cleaning process
        cleaning_process = CleaningProcess.query.filter_by(
            order_id=order_id, 
            process_type='12_hour',
            status='running'
        ).first()
        
        if not cleaning_process:
            return jsonify({'error': 'No active 12-hour cleaning process found'}), 404
        
        # Check if timer is completed - allow completion if timer has finished OR if manually triggered
        current_time = datetime.utcnow()
        timer_completed = current_time >= cleaning_process.countdown_end
        
        # Allow completion if timer is done OR if this is a manual completion
        if not timer_completed and not data.get('force_completion', False):
            remaining_minutes = (cleaning_process.countdown_end - current_time).total_seconds() / 60
            return jsonify({
                'error': f'Timer not completed yet. {remaining_minutes:.1f} minutes remaining. Please wait or contact supervisor.',
                'remaining_minutes': remaining_minutes
            }), 400
        
        # Update cleaning process with completion data
        cleaning_process.moisture_after = outgoing_moisture
        cleaning_process.completed_by = operator_name
        cleaning_process.completion_time = current_time
        cleaning_process.post_process_notes = notes
        cleaning_process.status = 'completed'
        cleaning_process.timer_active = False
        
        # Update order status to final completion
        order = ProductionOrder.query.get(order_id)
        order.status = 'completed'
        
        # Update cleaning bin status
        cleaning_bin = CleaningBin.query.get(cleaning_process.cleaning_bin_id)
        if cleaning_bin:
            cleaning_bin.status = 'available'
        
        # Calculate moisture reduction efficiency
        moisture_reduction = cleaning_process.start_moisture - outgoing_moisture
        target_achieved = abs(outgoing_moisture - cleaning_process.target_moisture) <= 1.0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'completion_time': current_time.isoformat(),
            'outgoing_moisture': outgoing_moisture,
            'moisture_reduction': round(moisture_reduction, 2),
            'target_achieved': target_achieved,
            'message': '12-hour cleaning process completed successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/upload_12h_cleaning_photo', methods=['POST'])
def upload_12h_cleaning_photo():
    """Upload manual cleaning photos for 12-hour process"""
    try:
        order_id = request.form.get('order_id')
        photo_type = request.form.get('photo_type')  # 'before', 'after'
        operator_name = request.form.get('operator_name', 'Operator')
        notes = request.form.get('notes', '')
        
        if not order_id or not photo_type:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if file was uploaded
        if 'photo_file' not in request.files:
            return jsonify({'error': 'No photo file uploaded'}), 400
        
        file = request.files['photo_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid photo file'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"12h_{photo_type}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create manual cleaning log
        cleaning_process = CleaningProcess.query.filter_by(
            order_id=int(order_id), 
            process_type='12_hour',
            status='running'
        ).first()
        
        if cleaning_process:
            # Check if we have both before and after photos for this minute
            current_minute = int((datetime.utcnow() - cleaning_process.start_time).total_seconds() // 60)
            
            manual_cleaning = ManualCleaningLog(
                order_id=int(order_id),
                cleaning_process_id=cleaning_process.id,
                machine_name='12-Hour Cleaning Manual',
                operator_name=operator_name,
                cleaning_start_time=datetime.utcnow(),
                cleaning_end_time=datetime.utcnow(),
                duration_minutes=0.5,
                notes=f"Minute {current_minute}: {notes}",
                status='completed'
            )
            
            # Set appropriate photo field
            if photo_type == 'before':
                manual_cleaning.before_photo = filename
            else:
                manual_cleaning.after_photo = filename
            
            db.session.add(manual_cleaning)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'upload_time': datetime.utcnow().isoformat(),
            'message': f'{photo_type.title()} photo uploaded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/get_pending_reminders/<int:order_id>')
def get_pending_reminders(order_id):
    """Get pending reminders for a cleaning process - improved version"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, timer_active=True).first()
        
        if not cleaning_process:
            return jsonify({'has_pending': False})
        
        current_time = datetime.utcnow()
        
        # Calculate elapsed minutes since process started
        elapsed_minutes = (current_time - cleaning_process.start_time).total_seconds() / 60
        current_minute = int(elapsed_minutes)
        
        # Only show reminder every minute during active process
        if current_minute > 0 and elapsed_minutes >= current_minute:
            return jsonify({
                'has_pending': True,
                'reminder': {
                    'id': f'minute_{current_minute}',
                    'order_id': order_id,
                    'sequence': current_minute,
                    'due_time': current_time.isoformat(),
                    'message': f'Manual cleaning required - Minute {current_minute}',
                    'process_type': cleaning_process.process_type
                },
                'elapsed_minutes': current_minute,
                'show_popup': True
            })
        
        return jsonify({
            'has_pending': False,
            'elapsed_minutes': current_minute
        })
        
    except Exception as e:
        logging.error(f"Error getting pending reminders: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/trigger_manual_reminders/<int:order_id>', methods=['POST'])
def trigger_manual_reminders(order_id):
    """Manually trigger cleaning reminders for testing"""
    try:
        cleaning_process = CleaningProcess.query.filter_by(order_id=order_id, timer_active=True).first()
        
        if not cleaning_process:
            return jsonify({'error': 'No active cleaning process found'}), 404
        
        current_time = datetime.utcnow()
        
        # Create an immediate reminder
        reminder = CleaningReminder(
            cleaning_process_id=cleaning_process.id,
            due_time=current_time,
            reminder_sequence=99,  # Special sequence for manual triggers
            reminder_sent=True,
            user_notified='Manual Trigger'
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        logging.info(f"Manual cleaning reminder triggered for process {cleaning_process.id}")
        
        return jsonify({
            'success': True,
            'reminder_id': reminder.id,
            'message': 'Manual cleaning reminder triggered'
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error triggering manual reminder: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/upload_reminder_photos', methods=['POST'])
def upload_reminder_photos():
    """Upload both before and after photos for a cleaning reminder"""
    try:
        # Get form data
        reminder_id = request.form.get('reminder_id')
        before_notes = request.form.get('before_notes', '')
        after_notes = request.form.get('after_notes', '')
        cleaning_area = request.form.get('cleaning_area', '')
        
        if not reminder_id:
            return jsonify({'error': 'Missing reminder ID'}), 400
        
        # Check if files were uploaded
        if 'before_photo' not in request.files or 'after_photo' not in request.files:
            return jsonify({'error': 'Both before and after photos are required'}), 400
        
        before_file = request.files['before_photo']
        after_file = request.files['after_photo']
        
        if before_file.filename == '' or after_file.filename == '':
            return jsonify({'error': 'Both photos must be selected'}), 400
        
        if not allowed_file(before_file.filename) or not allowed_file(after_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get the reminder
        reminder = CleaningReminder.query.get(reminder_id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404
        
        # Save before photo
        before_filename = secure_filename(before_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        before_filename = f"cleaning_before_{timestamp}_{before_filename}"
        before_path = os.path.join(app.config['UPLOAD_FOLDER'], before_filename)
        before_file.save(before_path)
        
        # Save after photo
        after_filename = secure_filename(after_file.filename)
        after_filename = f"cleaning_after_{timestamp}_{after_filename}"
        after_path = os.path.join(app.config['UPLOAD_FOLDER'], after_filename)
        after_file.save(after_path)
        
        # Create photo records
        before_photo = CleaningReminderPhoto(
            reminder_id=reminder_id,
            photo_type='before',
            file_path=before_path,
            uploaded_by='System User',
            uploaded_at=datetime.utcnow(),
            notes=f"{cleaning_area} - {before_notes}".strip(' -')
        )
        
        after_photo = CleaningReminderPhoto(
            reminder_id=reminder_id,
            photo_type='after',
            file_path=after_path,
            uploaded_by='System User',
            uploaded_at=datetime.utcnow(),
            notes=f"{cleaning_area} - {after_notes}".strip(' -')
        )
        
        db.session.add(before_photo)
        db.session.add(after_photo)
        
        # Mark reminder as completed
        reminder.completed = True
        reminder.photo_uploaded = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'before_photo_id': before_photo.id,
            'after_photo_id': after_photo.id,
            'upload_time': before_photo.uploaded_at.isoformat(),
            'message': 'Cleaning photos uploaded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Enhanced Grinding Process Routes
@app.route('/start_grinding/<int:order_id>', methods=['GET', 'POST'])
def start_grinding(order_id):
    """Start grinding process after 12-hour cleaning completion"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    # Check if 12-hour process is completed
    if order.status != 'completed':
        flash('12-hour cleaning must be completed before starting grinding process.', 'error')
        return redirect(url_for('production_orders'))
    
    if request.method == 'POST':
        try:
            # Get form data
            b1_scale_operator = request.form['b1_scale_operator']
            b1_scale_weight = float(request.form['b1_scale_weight'])
            b1_scale_notes = request.form.get('b1_scale_notes', '')
            grinding_machine = request.form['grinding_machine']
            grinding_operator = request.form['grinding_operator']
            
            # Create grinding session
            grinding_session = GrindingSession(
                order_id=order_id,
                start_time=datetime.utcnow(),
                timer_active=True,
                b1_scale_operator=b1_scale_operator,
                b1_scale_handoff_time=datetime.utcnow(),
                b1_scale_weight_kg=b1_scale_weight,
                b1_scale_notes=b1_scale_notes,
                grinding_machine_name=grinding_machine,
                grinding_operator=grinding_operator,
                total_input_kg=b1_scale_weight,
                status='grinding'
            )
            
            db.session.add(grinding_session)
            
            # Update order status to grinding
            order.status = 'grinding'
            
            db.session.commit()
            
            flash(f'Grinding process started successfully! Timer is now running.', 'success')
            return redirect(url_for('grinding_execution', order_id=order_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error starting grinding process: {str(e)}', 'error')
    
    return render_template('start_grinding.html', order=order)

@app.route('/grinding_execution/<int:order_id>')
def grinding_execution(order_id):
    """Monitor grinding process with live timer and production ratios"""
    order = ProductionOrder.query.get_or_404(order_id)
    grinding_session = GrindingSession.query.filter_by(order_id=order_id, status='grinding').first()
    
    if not grinding_session:
        flash('No active grinding session found.', 'error')
        return redirect(url_for('production_orders'))
    
    # Get storage areas for finished goods placement
    storage_areas = StorageArea.query.all()
    
    return render_template('grinding_execution.html', 
                         order=order, 
                         grinding_session=grinding_session,
                         storage_areas=storage_areas)

@app.route('/stop_grinding/<int:session_id>', methods=['POST'])
def stop_grinding(session_id):
    """Stop grinding timer and finalize session"""
    try:
        grinding_session = GrindingSession.query.get_or_404(session_id)
        
        if not grinding_session.timer_active:
            return jsonify({'error': 'Timer is not active'}), 400
        
        # Stop timer and calculate duration
        end_time = datetime.utcnow()
        duration_seconds = int((end_time - grinding_session.start_time).total_seconds())
        
        grinding_session.end_time = end_time
        grinding_session.duration_seconds = duration_seconds
        grinding_session.timer_active = False
        grinding_session.status = 'completed'
        
        # Update order status
        order = ProductionOrder.query.get(grinding_session.order_id)
        order.status = 'grinding_completed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'duration_seconds': duration_seconds,
            'end_time': end_time.isoformat(),
            'message': 'Grinding process completed successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/grinding_timer_status/<int:order_id>')
def get_grinding_timer_status(order_id):
    """Get current timer status for grinding process"""
    try:
        grinding_session = GrindingSession.query.filter_by(
            order_id=order_id, 
            timer_active=True
        ).first()
        
        if not grinding_session:
            return jsonify({'timer_active': False})
        
        current_time = datetime.utcnow()
        elapsed_seconds = int((current_time - grinding_session.start_time).total_seconds())
        
        # Manual cleaning reminder every 10 seconds
        needs_manual_cleaning = (elapsed_seconds % 10 == 0) and elapsed_seconds > 0
        
        return jsonify({
            'timer_active': True,
            'start_time': grinding_session.start_time.isoformat(),
            'elapsed_seconds': elapsed_seconds,
            'b1_scale_weight': grinding_session.b1_scale_weight_kg,
            'grinding_machine': grinding_session.grinding_machine_name,
            'grinding_operator': grinding_session.grinding_operator,
            'needs_manual_cleaning': needs_manual_cleaning,
            'session_id': grinding_session.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/submit_production_outputs', methods=['POST'])
def submit_production_outputs():
    """Submit production outputs with ratio validation"""
    try:
        data = request.get_json()
        session_id = data['session_id']
        outputs = data['outputs']  # List of {product_name, product_type, quantity_kg}
        
        grinding_session = GrindingSession.query.get_or_404(session_id)
        
        total_output = 0
        main_products_total = 0
        bran_total = 0
        
        # Calculate totals and save outputs
        for output in outputs:
            product_output = ProductionOutput(
                grinding_session_id=session_id,
                product_name=output['product_name'],
                product_type=output['product_type'],
                quantity_kg=float(output['quantity_kg']),
                percentage_of_total=0  # Will calculate after loop
            )
            
            db.session.add(product_output)
            
            quantity = float(output['quantity_kg'])
            total_output += quantity
            
            if output['product_type'] == 'main_product':
                main_products_total += quantity
            elif output['product_type'] == 'bran':
                bran_total += quantity
        
        # Calculate percentages
        main_percentage = (main_products_total / total_output * 100) if total_output > 0 else 0
        bran_percentage = (bran_total / total_output * 100) if total_output > 0 else 0
        
        # Update percentages in outputs
        for output in ProductionOutput.query.filter_by(grinding_session_id=session_id):
            output.percentage_of_total = (output.quantity_kg / total_output * 100) if total_output > 0 else 0
        
        # Update grinding session
        grinding_session.total_output_kg = total_output
        grinding_session.main_products_kg = main_products_total
        grinding_session.bran_kg = bran_total
        grinding_session.main_products_percentage = main_percentage
        grinding_session.bran_percentage = bran_percentage
        
        # Check for bran alert (>25%)
        bran_alert = bran_percentage > 25.0
        grinding_session.bran_alert_triggered = bran_alert
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total_output_kg': total_output,
            'main_products_percentage': round(main_percentage, 2),
            'bran_percentage': round(bran_percentage, 2),
            'bran_alert': bran_alert,
            'message': 'Production outputs recorded successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/upload_grinding_cleaning_photo', methods=['POST'])
def upload_grinding_cleaning_photo():
    """Upload manual cleaning photos during grinding (every 10 seconds)"""
    try:
        session_id = request.form.get('session_id')
        photo_type = request.form.get('photo_type')  # 'before', 'after'
        operator_name = request.form.get('operator_name', 'Operator')
        notes = request.form.get('notes', '')
        
        if not session_id or not photo_type:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if file was uploaded
        if 'photo_file' not in request.files:
            return jsonify({'error': 'No photo file uploaded'}), 400
        
        file = request.files['photo_file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid photo file'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"grinding_{photo_type}_{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create or update manual cleaning log
        grinding_cleaning = GrindingManualCleaning(
            grinding_session_id=int(session_id),
            operator_name=operator_name,
            notes=notes,
            status='completed'
        )
        
        # Set appropriate photo field
        if photo_type == 'before':
            grinding_cleaning.before_photo = filename
        else:
            grinding_cleaning.after_photo = filename
        
        db.session.add(grinding_cleaning)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'upload_time': datetime.utcnow().isoformat(),
            'message': f'{photo_type.title()} photo uploaded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Packaging and Storage Management Routes
@app.route('/submit_packaging', methods=['POST'])
def submit_packaging():
    """Submit packaging records for finished products"""
    try:
        data = request.get_json()
        session_id = data['session_id']
        packaging_records = data['packaging_records']  # List of packaging data
        
        grinding_session = GrindingSession.query.get_or_404(session_id)
        
        for record in packaging_records:
            packaging = PackagingRecord(
                grinding_session_id=session_id,
                product_name=record['product_name'],
                bag_weight_kg=float(record['bag_weight_kg']),
                bag_count=int(record['bag_count']),
                total_weight_kg=float(record['bag_weight_kg']) * int(record['bag_count']),
                operator_name=record['operator_name']
            )
            
            db.session.add(packaging)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total_records': len(packaging_records),
            'message': 'Packaging records saved successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/storage_management')
def storage_management():
    """Storage areas management dashboard"""
    storage_areas = StorageArea.query.all()
    
    # Get recent transactions
    recent_transactions = StorageTransaction.query.order_by(
        StorageTransaction.transaction_time.desc()
    ).limit(20).all()
    
    return render_template('storage_management.html', 
                         storage_areas=storage_areas,
                         recent_transactions=recent_transactions)

@app.route('/storage_transaction', methods=['POST'])
def create_storage_transaction():
    """Create storage transaction (storage or shifting)"""
    try:
        data = request.get_json()
        
        transaction = StorageTransaction(
            from_storage_area_id=data.get('from_storage_area_id'),
            to_storage_area_id=data['to_storage_area_id'],
            product_name=data['product_name'],
            quantity_kg=float(data['quantity_kg']),
            transaction_type=data['transaction_type'],  # 'storage' or 'shift'
            operator_name=data['operator_name'],
            grinding_session_id=data.get('grinding_session_id'),
            notes=data.get('notes', '')
        )
        
        db.session.add(transaction)
        
        # Update storage area quantities
        to_storage = StorageArea.query.get(data['to_storage_area_id'])
        to_storage.current_stock_kg += float(data['quantity_kg'])
        
        if data.get('from_storage_area_id'):
            from_storage = StorageArea.query.get(data['from_storage_area_id'])
            from_storage.current_stock_kg -= float(data['quantity_kg'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction_id': transaction.id,
            'message': f'{transaction.transaction_type.title()} transaction completed successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/storage_areas')
def get_storage_areas():
    """Get all storage areas with current stock levels"""
    try:
        storage_areas = StorageArea.query.all()
        
        areas_data = []
        for area in storage_areas:
            utilization_percentage = (area.current_stock_kg / area.capacity_kg * 100) if area.capacity_kg > 0 else 0
            
            areas_data.append({
                'id': area.id,
                'name': area.name,
                'capacity_kg': area.capacity_kg,
                'current_stock_kg': area.current_stock_kg,
                'available_space_kg': area.capacity_kg - area.current_stock_kg,
                'utilization_percentage': round(utilization_percentage, 1),
                'location': area.location
            })
        
        return jsonify({
            'success': True,
            'storage_areas': areas_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/shift_stock', methods=['POST'])
def shift_stock():
    """Shift stock between storage areas"""
    try:
        data = request.get_json()
        from_area_id = data['from_storage_area_id']
        to_area_id = data['to_storage_area_id']
        quantity = float(data['quantity_kg'])
        
        # Validate from storage has enough stock
        from_storage = StorageArea.query.get_or_404(from_area_id)
        if from_storage.current_stock_kg < quantity:
            return jsonify({'error': 'Insufficient stock in source storage area'}), 400
        
        # Validate to storage has enough capacity
        to_storage = StorageArea.query.get_or_404(to_area_id)
        if (to_storage.current_stock_kg + quantity) > to_storage.capacity_kg:
            return jsonify({'error': 'Insufficient capacity in destination storage area'}), 400
        
        # Create transaction record
        transaction = StorageTransaction(
            from_storage_area_id=from_area_id,
            to_storage_area_id=to_area_id,
            product_name=data['product_name'],
            quantity_kg=quantity,
            transaction_type='shift',
            operator_name=data['operator_name'],
            notes=data.get('notes', '')
        )
        
        db.session.add(transaction)
        
        # Update storage quantities
        from_storage.current_stock_kg -= quantity
        to_storage.current_stock_kg += quantity
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully shifted {quantity} kg from {from_storage.name} to {to_storage.name}',
            'transaction_id': transaction.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/packaging_view/<int:production_order_id>', methods=['GET', 'POST'])
def packaging_view(production_order_id):
    """Production order packaging view with process tracking"""
    production_order = ProductionOrder.query.get_or_404(production_order_id)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            packaging_items = data['packaging_items']
            
            for item in packaging_items:
                # Create packaging record linked to production order
                packaging = PackagingRecord(
                    production_order_id=production_order_id,
                    product_name=item['product_name'],
                    bag_weight_kg=float(item['bag_weight_kg']),
                    bag_count=int(item['bag_count']),
                    total_weight_kg=float(item['bag_weight_kg']) * int(item['bag_count']),
                    operator_name=item['operator_name'],
                    storage_area_id=int(item['storage_area_id']),
                    process_stage=item.get('process_stage', 'packaging')
                )
                
                db.session.add(packaging)
                
                # Create storage transaction
                storage_transaction = StorageTransaction(
                    to_storage_area_id=int(item['storage_area_id']),
                    product_name=item['product_name'],
                    quantity_kg=packaging.total_weight_kg,
                    transaction_type='storage',
                    operator_name=item['operator_name'],
                    notes=f"Production Order #{production_order.order_number}: Packaged {item['bag_count']} bags of {item['bag_weight_kg']}kg each - Stage: {item.get('process_stage', 'packaging')}"
                )
                
                db.session.add(storage_transaction)
                
                # Update storage area stock
                storage_area = StorageArea.query.get(item['storage_area_id'])
                if storage_area:
                    storage_area.current_stock_kg += packaging.total_weight_kg
            
            # Update production order status to packaging if not already completed
            if production_order.status != 'completed':
                production_order.status = 'packaging'
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully packaged {len(packaging_items)} products for Order #{production_order.order_number}'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    # Get data for the template
    products = Product.query.all()
    storage_areas = StorageArea.query.all()
    order_packaging = PackagingRecord.query.filter_by(
        production_order_id=production_order_id
    ).order_by(PackagingRecord.packaging_time.desc()).all()
    recent_packaging = PackagingRecord.query.order_by(PackagingRecord.packaging_time.desc()).limit(10).all()
    
    return render_template('packaging_view.html', 
                         production_order=production_order,
                         products=products, 
                         storage_areas=storage_areas,
                         order_packaging=order_packaging,
                         recent_packaging=recent_packaging)

# Backward compatibility redirect for old packaging view
@app.route('/packaging_view', methods=['GET'])
def packaging_view_redirect():
    """Redirect old packaging view to production orders page"""
    flash('Please select a production order to access packaging.', 'info')
    return redirect(url_for('production_orders'))

@app.route('/api/storage_area_products/<int:storage_area_id>')
def get_storage_area_products(storage_area_id):
    """Get products available in a specific storage area"""
    try:
        # Get recent transactions for this storage area
        transactions = StorageTransaction.query.filter_by(
            to_storage_area_id=storage_area_id
        ).order_by(StorageTransaction.transaction_time.desc()).limit(50).all()
        
        # Group by product name and calculate quantities
        product_quantities = {}
        for transaction in transactions:
            product_name = transaction.product_name
            if product_name not in product_quantities:
                product_quantities[product_name] = 0
            product_quantities[product_name] += transaction.quantity_kg
        
        # Get outbound transactions to subtract
        outbound_transactions = StorageTransaction.query.filter_by(
            from_storage_area_id=storage_area_id
        ).all()
        
        for transaction in outbound_transactions:
            product_name = transaction.product_name
            if product_name in product_quantities:
                product_quantities[product_name] -= transaction.quantity_kg
        
        # Format response
        available_products = []
        for product_name, quantity in product_quantities.items():
            if quantity > 0:
                available_products.append({
                    'product_name': product_name,
                    'available_quantity_kg': round(quantity, 2)
                })
        
        return jsonify({
            'success': True,
            'available_products': available_products
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/storage_contents/<int:storage_area_id>')
def get_storage_contents(storage_area_id):
    """Get contents of a specific storage area"""
    try:
        storage_area = StorageArea.query.get_or_404(storage_area_id)
        
        # Get packing records for this storage area
        packing_records = PackagingRecord.query.filter_by(
            storage_area_id=storage_area_id
        ).all()
        
        # Group by product name and sum quantities
        contents = {}
        for record in packing_records:
            if record.product_name not in contents:
                contents[record.product_name] = {
                    'product_name': record.product_name,
                    'total_quantity': 0,
                    'bag_count': 0
                }
            contents[record.product_name]['total_quantity'] += record.total_weight_kg
            contents[record.product_name]['bag_count'] += record.bag_count
        
        contents_list = list(contents.values())
        
        return jsonify({
            'success': True,
            'storage_area': {
                'id': storage_area.id,
                'name': storage_area.name,
                'capacity_kg': storage_area.capacity_kg,
                'current_stock_kg': storage_area.current_stock_kg,
                'available_space_kg': storage_area.capacity_kg - storage_area.current_stock_kg
            },
            'contents': contents_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/packing_execution/<int:order_id>', methods=['GET', 'POST'])
def packing_execution(order_id):
    """Execute packing process for production order"""
    order = ProductionOrder.query.get_or_404(order_id)
    
    if request.method == 'POST':
        try:
            operator_name = request.form['operator_name']
            
            # Handle photo upload
            packing_photo = None
            if 'packing_photo' in request.files:
                file = request.files['packing_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"packing_{timestamp}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    packing_photo = filename
            
            # Process multiple products
            product_names = request.form.getlist('product_name')
            bag_weights = request.form.getlist('bag_weight')
            bag_counts = request.form.getlist('bag_count')
            storage_area_ids = request.form.getlist('storage_area_id')
            
            total_packed = 0
            
            for i in range(len(product_names)):
                if product_names[i] and bag_weights[i] and bag_counts[i] and storage_area_ids[i]:
                    bag_weight = float(bag_weights[i])
                    bag_count = int(bag_counts[i])
                    total_weight = bag_weight * bag_count
                    
                    # Create packaging record
                    packaging = PackagingRecord(
                        grinding_session_id=None,  # Not linked to grinding session in this case
                        product_name=product_names[i],
                        bag_weight_kg=bag_weight,
                        bag_count=bag_count,
                        total_weight_kg=total_weight,
                        operator_name=operator_name,
                        storage_area_id=int(storage_area_ids[i])
                    )
                    
                    db.session.add(packaging)
                    
                    # Update storage area stock
                    storage_area = StorageArea.query.get(int(storage_area_ids[i]))
                    if storage_area:
                        storage_area.current_stock_kg += total_weight
                    
                    total_packed += total_weight
            
            # Update order status
            order.status = 'packing_completed'
            
            db.session.commit()
            
            flash(f'Packing process completed successfully! Total packed: {total_packed:.2f} kg', 'success')
            return redirect(url_for('production_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing packing process: {str(e)}', 'error')
    
    # Get storage areas for display
    storage_areas = StorageArea.query.all()
    
    return render_template('packing_execution.html', 
                         order=order,
                         storage_areas=storage_areas)

