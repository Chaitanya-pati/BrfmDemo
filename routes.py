import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import (Supplier, Vehicle, QualityTest, GodownType, Godown, 
                    Transfer, PrecleaningBin, CleaningMachine, CleaningLog, ProductionOrder, 
                    ProductionPlan, ProductionPlanItem, ProductionJobNew, FinishedGoodsStorage, 
                    FinishedGoods, Product, Customer, SalesOrder, SalesOrderItem, DispatchVehicle, 
                    Dispatch, DispatchItem, User, CleaningReminder, ProductionTransfer, CleaningProcess,
                    GrindingProcess, ProductOutput, PackingProcess, StorageArea, StorageTransfer, ProcessReminder)
from utils import allowed_file, generate_order_number, generate_job_id, calculate_production_percentages
import logging

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
    precleaning_bins = PrecleaningBin.query.all()
    return render_template('godown_management.html', godowns=godowns, precleaning_bins=precleaning_bins)

@app.route('/precleaning', methods=['GET', 'POST'])
def precleaning():
    if request.method == 'POST':
        try:
            # Handle evidence photo
            evidence_photo = None
            if 'evidence_photo' in request.files:
                file = request.files['evidence_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    evidence_photo = filename
            
            from_godown_id = request.form['from_godown_id']
            to_precleaning_bin_id = request.form['to_precleaning_bin_id']
            quantity = float(request.form['quantity'])
            
            # Check if enough stock in godown
            godown = Godown.query.get(from_godown_id)
            if godown and godown.current_stock < quantity:
                flash('Insufficient stock in selected godown!', 'error')
                return redirect(url_for('precleaning'))
            
            # Create transfer record
            transfer = Transfer()
            transfer.from_godown_id = int(from_godown_id)
            transfer.to_precleaning_bin_id = int(to_precleaning_bin_id)
            transfer.quantity = quantity
            transfer.transfer_type = 'godown_to_precleaning'
            transfer.operator = request.form['operator']
            transfer.evidence_photo = evidence_photo
            transfer.notes = request.form.get('notes')
            
            # Update inventories
            if godown:
                godown.current_stock -= quantity
            precleaning_bin = PrecleaningBin.query.get(to_precleaning_bin_id)
            if precleaning_bin:
                precleaning_bin.current_stock += quantity
            
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
            order.order_number = generate_order_number()
            order.customer_id = int(request.form['customer_id']) if request.form.get('customer_id') else None
            order.quantity = float(request.form['quantity'])
            order.product_id = int(request.form['product_id'])
            order.description = request.form.get('description')
            order.created_by = request.form['created_by']
            order.target_completion = datetime.strptime(request.form['target_completion'], '%Y-%m-%d') if request.form.get('target_completion') else None
            
            db.session.add(order)
            db.session.commit()
            flash('Production order created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production order: {str(e)}', 'error')
    
    customers = Customer.query.all()
    products = Product.query.filter_by(category='Main Product').all()
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    
    return render_template('production_orders.html', customers=customers, products=products, orders=orders)

@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id):
    order = ProductionOrder.query.get_or_404(order_id)
    
    if request.method == 'POST':
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
    
    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()
    
    return render_template('production_planning.html', order=order, precleaning_bins=precleaning_bins, existing_plan=existing_plan)

@app.route('/cleaning_management', methods=['GET', 'POST'])
def cleaning_management():
    if request.method == 'POST':
        try:
            # Handle cleaning log photos
            photo_before = None
            photo_after = None
            
            if 'photo_before' in request.files:
                file = request.files['photo_before']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"before_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photo_before = filename
            
            if 'photo_after' in request.files:
                file = request.files['photo_after']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
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
        if request.form.get('action') == 'create_order':
            try:
                sales_order = SalesOrder()
                sales_order.order_number = generate_order_number('SO')
                sales_order.customer_id = int(request.form['customer_id'])
                sales_order.salesman = request.form['salesman']
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
                        filename = f"loading_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loading_photo = filename
                
                if 'loaded_photo' in request.files:
                    file = request.files['loaded_photo']
                    if file and file.filename and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loaded_photo = filename
                
                dispatch = Dispatch()
                dispatch.dispatch_number = generate_order_number('DP')
                dispatch.sales_order_id = int(request.form['sales_order_id'])
                dispatch.vehicle_id = int(request.form['vehicle_id'])
                dispatch.quantity = float(request.form['quantity'])
                dispatch.loading_photo = loading_photo
                dispatch.loaded_photo = loaded_photo
                
                # Update sales order quantities
                sales_order = SalesOrder.query.get(request.form['sales_order_id'])
                if sales_order:
                    sales_order.delivered_quantity += float(request.form['quantity'])
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
    
    customers = Customer.query.all()
    vehicles = DispatchVehicle.query.filter_by(status='available').all()
    sales_orders = SalesOrder.query.filter(SalesOrder.status.in_(['pending', 'partial'])).all()
    dispatches = Dispatch.query.order_by(Dispatch.dispatch_date.desc()).all()
    
    return render_template('sales_dispatch.html', customers=customers, vehicles=vehicles, 
                         sales_orders=sales_orders, dispatches=dispatches)

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
    
    dispatch_stats = db.session.query(
        Dispatch.status,
        db.func.count(Dispatch.id).label('count')
    ).group_by(Dispatch.status).all()
    
    return render_template('reports.html', 
                         vehicle_stats=vehicle_stats,
                         godown_inventory=godown_inventory,
                         production_stats=production_stats,
                         dispatch_stats=dispatch_stats)

@app.route('/masters', methods=['GET', 'POST'])
def masters():
    if request.method == 'POST':
        try:
            form_type = request.form.get('form_type')
            
            if form_type == 'supplier':
                supplier = Supplier()
                supplier.company_name = request.form['name']
                supplier.contact_person = request.form.get('contact_person')
                supplier.phone = request.form.get('phone')
                supplier.address = request.form.get('address')
                db.session.add(supplier)
                
            elif form_type == 'customer':
                customer = Customer()
                customer.company_name = request.form['name']
                customer.contact_person = request.form.get('contact_person')
                customer.phone = request.form.get('phone')
                customer.email = request.form.get('email')
                customer.address = request.form.get('address')
                customer.city = request.form.get('city')
                customer.state = request.form.get('state')
                customer.postal_code = request.form.get('postal_code')
                db.session.add(customer)
                
            elif form_type == 'godown':
                godown = Godown()
                godown.name = request.form['name']
                godown.type_id = int(request.form['type_id'])
                godown.capacity = float(request.form.get('capacity', 0))
                db.session.add(godown)
                
            elif form_type == 'precleaning_bin':
                bin = PrecleaningBin()
                bin.name = request.form['name']
                bin.capacity = float(request.form['capacity'])
                db.session.add(bin)
                
            elif form_type == 'product':
                product = Product()
                product.name = request.form['name']
                product.category = request.form['category']
                product.description = request.form.get('description')
                db.session.add(product)
                
            elif form_type == 'cleaning_machine':
                machine = CleaningMachine()
                machine.name = request.form['name']
                machine.machine_type = request.form['machine_type']
                machine.cleaning_frequency_hours = int(request.form.get('cleaning_frequency_hours', 3))
                machine.location = request.form.get('location')
                db.session.add(machine)
                
            elif form_type == 'dispatch_vehicle':
                vehicle = DispatchVehicle()
                vehicle.vehicle_number = request.form['vehicle_number']
                vehicle.driver_name = request.form.get('driver_name')
                vehicle.driver_phone = request.form.get('driver_phone')
                vehicle.state = request.form.get('state')
                vehicle.city = request.form.get('city')
                vehicle.capacity = float(request.form.get('capacity', 0))
                db.session.add(vehicle)
            
            db.session.commit()
            flash('Record added successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding record: {str(e)}', 'error')
    
    # Get all master data
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    godown_types = GodownType.query.all()
    godowns = Godown.query.all()
    precleaning_bins = PrecleaningBin.query.all()
    products = Product.query.all()
    cleaning_machines = CleaningMachine.query.all()
    dispatch_vehicles = DispatchVehicle.query.all()
    
    return render_template('masters.html',
                         suppliers=suppliers, customers=customers,
                         godown_types=godown_types, godowns=godowns,
                         precleaning_bins=precleaning_bins, products=products,
                         cleaning_machines=cleaning_machines, dispatch_vehicles=dispatch_vehicles)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
                
            elif action == 'execute_transfer':
                # Execute transfer from precleaning bins to 24h cleaning
                job_id = int(request.form['job_id'])
                from_bin_id = int(request.form['from_bin_id'])
                transfer_quantity = float(request.form['transfer_quantity'])
                operator_name = request.form['operator_name']
                
                # Handle photo uploads
                start_photo = None
                end_photo = None
                
                if 'transfer_start_photo' in request.files:
                    file = request.files['transfer_start_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"transfer_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        start_photo = filename
                
                if 'transfer_end_photo' in request.files:
                    file = request.files['transfer_end_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"transfer_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        end_photo = filename
                
                # Create transfer record
                transfer = ProductionTransfer()
                transfer.job_id = job_id
                transfer.from_precleaning_bin_id = from_bin_id
                transfer.quantity_transferred = transfer_quantity
                transfer.operator_name = operator_name
                transfer.start_photo = start_photo
                transfer.end_photo = end_photo
                transfer.transfer_time = datetime.now()
                
                # Update bin stock
                bin = PrecleaningBin.query.get(from_bin_id)
                bin.current_stock -= transfer_quantity
                
                # Update job status
                job = ProductionJobNew.query.get(job_id)
                job.status = 'in_progress'
                job.started_at = datetime.now()
                
                db.session.add(transfer)
                db.session.commit()
                
                flash('Transfer executed successfully!', 'success')
                
            elif action == 'start_cleaning':
                # Start 24h or 12h cleaning process
                job_id = int(request.form['job_id'])
                process_type = request.form['process_type']  # 24_hour or 12_hour
                duration_hours = int(request.form['duration_hours'])
                cleaning_bin_id = int(request.form['cleaning_bin_id'])
                operator_name = request.form['operator_name']
                target_moisture = request.form.get('target_moisture')
                
                start_time = datetime.now()
                end_time = start_time + timedelta(hours=duration_hours)
                
                # Handle photo uploads
                start_photo = None
                if 'cleaning_start_photo' in request.files:
                    file = request.files['cleaning_start_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"cleaning_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        start_photo = filename
                
                cleaning = CleaningProcess()
                cleaning.job_id = job_id
                cleaning.process_type = process_type
                cleaning.cleaning_bin_id = cleaning_bin_id
                cleaning.duration_hours = duration_hours
                cleaning.start_time = start_time
                cleaning.end_time = end_time
                cleaning.target_moisture = float(target_moisture) if target_moisture else None
                cleaning.operator_name = operator_name
                cleaning.start_photo = start_photo
                cleaning.status = 'running'
                
                # Create reminders (5min, 10min, 30min before completion)
                for minutes_before in [5, 10, 30]:
                    reminder_time = end_time - timedelta(minutes=minutes_before)
                    if reminder_time > datetime.now():
                        reminder = ProcessReminder()
                        reminder.job_id = job_id
                        reminder.process_type = f'cleaning_{process_type}'
                        reminder.reminder_time = reminder_time
                        reminder.reminder_type = f'{minutes_before}min'
                        reminder.message = f'{process_type} cleaning process will complete in {minutes_before} minutes'
                        db.session.add(reminder)
                
                db.session.add(cleaning)
                db.session.commit()
                
                flash(f'{process_type} cleaning process started successfully!', 'success')
                
            elif action == 'start_grinding':
                # Start grinding process
                job_id = int(request.form['job_id'])
                machine_name = request.form['machine_name']
                input_quantity = float(request.form['input_quantity'])
                operator_name = request.form['operator_name']
                
                # Handle photo uploads
                start_photo = None
                if 'grinding_start_photo' in request.files:
                    file = request.files['grinding_start_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"grinding_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        start_photo = filename
                
                grinding = GrindingProcess()
                grinding.job_id = job_id
                grinding.machine_name = machine_name
                grinding.input_quantity_kg = input_quantity
                grinding.start_time = datetime.now()
                grinding.operator_name = operator_name
                grinding.start_photo = start_photo
                grinding.status = 'pending'
                
                db.session.add(grinding)
                db.session.commit()
                
                flash('Grinding process started successfully!', 'success')
                
            elif action == 'complete_grinding':
                # Complete grinding process with outputs
                grinding_id = int(request.form['grinding_id'])
                total_output = float(request.form['total_output'])
                main_products = float(request.form['main_products'])
                bran_kg = float(request.form['bran_kg'])
                
                grinding = GrindingProcess.query.get(grinding_id)
                grinding.total_output_kg = total_output
                grinding.main_products_kg = main_products
                grinding.bran_kg = bran_kg
                grinding.bran_percentage = (bran_kg / total_output) * 100
                grinding.end_time = datetime.now()
                grinding.status = 'completed'
                
                # Check bran percentage (should be 23-25%)
                if grinding.bran_percentage > 25:
                    flash(f'Warning: Bran percentage ({grinding.bran_percentage:.1f}%) is higher than expected (23-25%)', 'warning')
                
                # Handle photo uploads
                if 'grinding_end_photo' in request.files:
                    file = request.files['grinding_end_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"grinding_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        grinding.end_photo = filename
                
                db.session.commit()
                flash('Grinding process completed successfully!', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    # Get data for the template
    active_production_jobs = ProductionJobNew.query.filter(
        ProductionJobNew.status.in_(['pending', 'in_progress', 'paused'])
    ).order_by(ProductionJobNew.created_at.desc()).all()
    
    approved_plans = ProductionPlan.query.filter_by(status='approved').all()
    transfer_jobs = ProductionJobNew.query.filter_by(stage='transfer', status='pending').all()
    precleaning_bins = PrecleaningBin.query.all()
    
    # Count active jobs by stage
    active_jobs = {}
    for stage in ['transfer', 'cleaning_24h', 'cleaning_12h', 'grinding', 'packing']:
        active_jobs[stage] = ProductionJobNew.query.filter_by(stage=stage, status='in_progress').count()
    
    completed_jobs = ProductionJobNew.query.filter_by(status='completed').count()
    
    # Get pending reminders
    pending_reminders = ProcessReminder.query.filter_by(status='pending').order_by(ProcessReminder.reminder_time).all()
    
    return render_template('production_execution.html',
                         active_production_jobs=active_production_jobs,
                         approved_plans=approved_plans,
                         transfer_jobs=transfer_jobs,
                         precleaning_bins=precleaning_bins,
                         active_jobs=active_jobs,
                         completed_jobs=completed_jobs,
                         pending_reminders=pending_reminders)

# API endpoints for production execution
@app.route('/api/production_job/<int:job_id>')
def get_production_job(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    # Calculate progress based on stage
    progress = 0
    if job.status == 'completed':
        progress = 100
    elif job.status == 'in_progress':
        if job.stage == 'transfer':
            # Count completed transfers vs planned
            completed_transfers = len(job.transfers)
            total_plan_items = len(job.plan.plan_items)
            progress = (completed_transfers / total_plan_items) * 100 if total_plan_items > 0 else 0
        elif job.stage in ['cleaning_24h', 'cleaning_12h']:
            # Calculate time-based progress
            cleaning_process = CleaningProcess.query.filter_by(job_id=job_id).first()
            if cleaning_process and cleaning_process.status == 'running':
                total_duration = (cleaning_process.end_time - cleaning_process.start_time).total_seconds()
                elapsed = (datetime.now() - cleaning_process.start_time).total_seconds()
                progress = min((elapsed / total_duration) * 100, 100)
        elif job.stage == 'grinding':
            grinding_process = GrindingProcess.query.filter_by(job_id=job_id).first()
            progress = 50 if grinding_process and grinding_process.status == 'pending' else 90
    
    return jsonify({
        'id': job.id,
        'job_number': job.job_number,
        'order_number': job.order.order_number,
        'stage': job.stage,
        'status': job.status,
        'progress': round(progress, 1),
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'started_by': job.started_by,
        'timeline': get_job_timeline(job_id)
    })

def get_job_timeline(job_id):
    job = ProductionJobNew.query.get(job_id)
    timeline = []
    
    if job.started_at:
        timeline.append({
            'stage': 'Job Started',
            'time': job.started_at.isoformat(),
            'status': 'completed',
            'operator': job.started_by
        })
    
    # Add transfer events
    for transfer in job.transfers:
        timeline.append({
            'stage': f'Transfer from {transfer.from_bin.name}',
            'time': transfer.transfer_time.isoformat(),
            'status': 'completed',
            'operator': transfer.operator_name,
            'quantity': f'{transfer.quantity_transferred} kg'
        })
    
    # Add cleaning events
    for cleaning in job.cleaning_processes:
        timeline.append({
            'stage': f'{cleaning.process_type} Cleaning',
            'time': cleaning.start_time.isoformat(),
            'status': cleaning.status,
            'operator': cleaning.operator_name,
            'end_time': cleaning.actual_end_time.isoformat() if cleaning.actual_end_time else cleaning.end_time.isoformat()
        })
    
    # Add grinding events
    for grinding in job.grinding_processes:
        timeline.append({
            'stage': 'Grinding',
            'time': grinding.start_time.isoformat(),
            'status': grinding.status,
            'operator': grinding.operator_name,
            'machine': grinding.machine_name
        })
    
    return timeline

@app.route('/api/start_job', methods=['POST'])
def start_job_api():
    try:
        data = request.get_json()
        job_id = data['job_id']
        
        job = ProductionJobNew.query.get_or_404(job_id)
        job.status = 'in_progress'
        job.started_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Job started successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/pause_job', methods=['POST'])
def pause_job_api():
    try:
        data = request.get_json()
        job_id = data['job_id']
        
        job = ProductionJobNew.query.get_or_404(job_id)
        job.status = 'paused'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Job paused successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/job_progress')
def job_progress_api():
    jobs = ProductionJobNew.query.filter_by(status='in_progress').all()
    progress_data = []
    
    for job in jobs:
        progress = 0
        # Calculate progress based on job stage and current status
        if job.stage == 'cleaning_24h' or job.stage == 'cleaning_12h':
            cleaning = CleaningProcess.query.filter_by(job_id=job.id).first()
            if cleaning and cleaning.status == 'running':
                total_duration = (cleaning.end_time - cleaning.start_time).total_seconds()
                elapsed = (datetime.now() - cleaning.start_time).total_seconds()
                progress = min((elapsed / total_duration) * 100, 100)
        
        progress_data.append({
            'id': job.id,
            'progress': round(progress, 1)
        })
    
    return jsonify(progress_data)

@app.route('/api/check_reminders')
def check_reminders_api():
    current_time = datetime.now()
    new_reminders = ProcessReminder.query.filter(
        ProcessReminder.reminder_time <= current_time,
        ProcessReminder.status == 'pending'
    ).count()
    
    return jsonify({'new_reminders': new_reminders})

@app.route('/api/godown_stock/<int:godown_id>')
def godown_stock(godown_id):
    godown = Godown.query.get_or_404(godown_id)
    return jsonify({'current_stock': godown.current_stock})

@app.route('/api/precleaning_stock/<int:bin_id>')
def precleaning_stock(bin_id):
    bin = PrecleaningBin.query.get_or_404(bin_id)
    return jsonify({'current_stock': bin.current_stock})

# Initialize sample data
@app.route('/init_data')
def init_data():
    try:
        # Create godown types
        if not GodownType.query.first():
            mill_type = GodownType()
            mill_type.name = 'Mill'
            mill_type.description = 'Regular mill quality wheat'
            db.session.add(mill_type)
            
            low_mill_type = GodownType()
            low_mill_type.name = 'Low Mill'
            low_mill_type.description = 'Lower quality wheat'
            db.session.add(low_mill_type)
            
            hd_type = GodownType()
            hd_type.name = 'HD'
            hd_type.description = 'High density wheat'
            db.session.add(hd_type)
        
        # Create sample products
        if not Product.query.first():
            maida = Product()
            maida.name = 'Maida'
            maida.category = 'Main Product'
            maida.description = 'Refined wheat flour'
            db.session.add(maida)
            
            suji = Product()
            suji.name = 'Suji'
            suji.category = 'Main Product'
            suji.description = 'Semolina'
            db.session.add(suji)
            
            chakki_ata = Product()
            chakki_ata.name = 'Chakki Ata'
            chakki_ata.category = 'Main Product'
            chakki_ata.description = 'Whole wheat flour'
            db.session.add(chakki_ata)
            
            tandoori_ata = Product()
            tandoori_ata.name = 'Tandoori Ata'
            tandoori_ata.category = 'Main Product'
            tandoori_ata.description = 'Special tandoori flour'
            db.session.add(tandoori_ata)
            
            bran = Product()
            bran.name = 'Bran'
            bran.category = 'Bran'
            bran.description = 'Wheat bran by-product'
            db.session.add(bran)
        
        # Create cleaning machines
        if not CleaningMachine.query.first():
            drum_shield = CleaningMachine()
            drum_shield.name = 'Drum Shield 1'
            drum_shield.machine_type = 'drum_shield'
            drum_shield.location = 'Pre-cleaning area'
            db.session.add(drum_shield)
            
            magnet = CleaningMachine()
            magnet.name = 'Magnet Machine 1'
            magnet.machine_type = 'magnet'
            magnet.location = 'Pre-cleaning area'
            db.session.add(magnet)
            
            separator = CleaningMachine()
            separator.name = 'Separator 1'
            separator.machine_type = 'separator'
            separator.location = 'Pre-cleaning area'
            db.session.add(separator)
            
            grinding = CleaningMachine()
            grinding.name = 'Grinding Machine'
            grinding.machine_type = 'grinding'
            grinding.cleaning_frequency_hours = 1
            grinding.location = 'Production area'
            db.session.add(grinding)
        
        db.session.commit()
        flash('Sample data initialized successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error initializing data: {str(e)}', 'error')
    
    return redirect(url_for('index'))
