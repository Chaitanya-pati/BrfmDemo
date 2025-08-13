import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from models import *
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
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bill_photo = filename
            
            if 'vehicle_photo' in request.files:
                file = request.files['vehicle_photo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"vehicle_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    vehicle_photo = filename
            
            vehicle = Vehicle(
                vehicle_number=request.form['vehicle_number'],
                supplier_id=request.form['supplier_id'],
                driver_name=request.form.get('driver_name'),
                driver_phone=request.form.get('driver_phone'),
                bill_photo=bill_photo,
                vehicle_photo_before=vehicle_photo,
                arrival_time=datetime.now()
            )
            
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
            
            quality_test = QualityTest(
                vehicle_id=vehicle_id,
                sample_bags_tested=request.form['sample_bags_tested'],
                total_bags=request.form['total_bags'],
                category_assigned=request.form['category_assigned'],
                moisture_content=request.form.get('moisture_content'),
                quality_notes=request.form.get('quality_notes'),
                lab_instructor=request.form['lab_instructor']
            )
            
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
                if file and file.filename != '' and allowed_file(file.filename):
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
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    evidence_photo = filename
            
            from_godown_id = request.form['from_godown_id']
            to_precleaning_bin_id = request.form['to_precleaning_bin_id']
            quantity = float(request.form['quantity'])
            
            # Check if enough stock in godown
            godown = Godown.query.get(from_godown_id)
            if godown.current_stock < quantity:
                flash('Insufficient stock in selected godown!', 'error')
                return redirect(url_for('precleaning'))
            
            # Create transfer record
            transfer = Transfer(
                from_godown_id=from_godown_id,
                to_precleaning_bin_id=to_precleaning_bin_id,
                quantity=quantity,
                transfer_type='godown_to_precleaning',
                operator=request.form['operator'],
                evidence_photo=evidence_photo,
                notes=request.form.get('notes')
            )
            
            # Update inventories
            godown.current_stock -= quantity
            precleaning_bin = PrecleaningBin.query.get(to_precleaning_bin_id)
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
            order = ProductionOrder(
                order_number=generate_order_number(),
                customer_id=request.form.get('customer_id'),
                quantity=float(request.form['quantity']),
                product_id=request.form['product_id'],
                description=request.form.get('description'),
                created_by=request.form['created_by'],
                target_completion=datetime.strptime(request.form['target_completion'], '%Y-%m-%d') if request.form.get('target_completion') else None
            )
            
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
            plan = ProductionPlan(
                order_id=order_id,
                planned_by=request.form['planned_by']
            )
            db.session.add(plan)
            db.session.flush()  # Get the plan ID
            
            total_percentage = 0
            precleaning_bins = request.form.getlist('precleaning_bin_id')
            percentages = request.form.getlist('percentage')
            
            for i, bin_id in enumerate(precleaning_bins):
                if bin_id and percentages[i]:
                    percentage = float(percentages[i])
                    quantity = (percentage / 100) * order.quantity
                    
                    plan_item = ProductionPlanItem(
                        plan_id=plan.id,
                        precleaning_bin_id=int(bin_id),
                        percentage=percentage,
                        quantity=quantity
                    )
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
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"before_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photo_before = filename
            
            if 'photo_after' in request.files:
                file = request.files['photo_after']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"after_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photo_after = filename
            
            cleaning_log = CleaningLog(
                machine_id=request.form['machine_id'],
                cleaned_by=request.form['cleaned_by'],
                photo_before=photo_before,
                photo_after=photo_after,
                waste_collected=float(request.form.get('waste_collected', 0)),
                notes=request.form.get('notes')
            )
            
            # Update machine's last cleaned time
            machine = CleaningMachine.query.get(request.form['machine_id'])
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
                sales_order = SalesOrder(
                    order_number=generate_order_number('SO'),
                    customer_id=request.form['customer_id'],
                    salesman=request.form['salesman'],
                    delivery_date=datetime.strptime(request.form['delivery_date'], '%Y-%m-%d'),
                    total_quantity=float(request.form['total_quantity']),
                    pending_quantity=float(request.form['total_quantity'])
                )
                
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
                    if file and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"loading_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loading_photo = filename
                
                if 'loaded_photo' in request.files:
                    file = request.files['loaded_photo']
                    if file and file.filename != '' and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        loaded_photo = filename
                
                dispatch = Dispatch(
                    dispatch_number=generate_order_number('DP'),
                    sales_order_id=request.form['sales_order_id'],
                    vehicle_id=request.form['vehicle_id'],
                    quantity=float(request.form['quantity']),
                    loading_photo=loading_photo,
                    loaded_photo=loaded_photo
                )
                
                # Update sales order quantities
                sales_order = SalesOrder.query.get(request.form['sales_order_id'])
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
                supplier = Supplier(
                    name=request.form['name'],
                    contact_person=request.form.get('contact_person'),
                    phone=request.form.get('phone'),
                    address=request.form.get('address')
                )
                db.session.add(supplier)
                
            elif form_type == 'customer':
                customer = Customer(
                    name=request.form['name'],
                    contact_person=request.form.get('contact_person'),
                    phone=request.form.get('phone'),
                    email=request.form.get('email'),
                    address=request.form.get('address'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    postal_code=request.form.get('postal_code')
                )
                db.session.add(customer)
                
            elif form_type == 'godown':
                godown = Godown(
                    name=request.form['name'],
                    type_id=request.form['type_id'],
                    capacity=float(request.form.get('capacity', 0))
                )
                db.session.add(godown)
                
            elif form_type == 'precleaning_bin':
                bin = PrecleaningBin(
                    name=request.form['name'],
                    capacity=float(request.form['capacity'])
                )
                db.session.add(bin)
                
            elif form_type == 'product':
                product = Product(
                    name=request.form['name'],
                    category=request.form['category'],
                    description=request.form.get('description')
                )
                db.session.add(product)
                
            elif form_type == 'cleaning_machine':
                machine = CleaningMachine(
                    name=request.form['name'],
                    machine_type=request.form['machine_type'],
                    cleaning_frequency_hours=int(request.form.get('cleaning_frequency_hours', 3)),
                    location=request.form.get('location')
                )
                db.session.add(machine)
                
            elif form_type == 'dispatch_vehicle':
                vehicle = DispatchVehicle(
                    vehicle_number=request.form['vehicle_number'],
                    driver_name=request.form.get('driver_name'),
                    driver_phone=request.form.get('driver_phone'),
                    state=request.form.get('state'),
                    city=request.form.get('city'),
                    capacity=float(request.form.get('capacity', 0))
                )
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
            types = [
                GodownType(name='Mill', description='Regular mill quality wheat'),
                GodownType(name='Low Mill', description='Lower quality wheat'),
                GodownType(name='HD', description='High density wheat')
            ]
            for t in types:
                db.session.add(t)
        
        # Create sample products
        if not Product.query.first():
            products = [
                Product(name='Maida', category='Main Product', description='Refined wheat flour'),
                Product(name='Suji', category='Main Product', description='Semolina'),
                Product(name='Chakki Ata', category='Main Product', description='Whole wheat flour'),
                Product(name='Tandoori Ata', category='Main Product', description='Special tandoori flour'),
                Product(name='Bran', category='Bran', description='Wheat bran by-product')
            ]
            for p in products:
                db.session.add(p)
        
        # Create cleaning machines
        if not CleaningMachine.query.first():
            machines = [
                CleaningMachine(name='Drum Shield 1', machine_type='drum_shield', location='Pre-cleaning area'),
                CleaningMachine(name='Magnet Machine 1', machine_type='magnet', location='Pre-cleaning area'),
                CleaningMachine(name='Separator 1', machine_type='separator', location='Pre-cleaning area'),
                CleaningMachine(name='Grinding Machine', machine_type='grinding', cleaning_frequency_hours=1, location='Production area')
            ]
            for m in machines:
                db.session.add(m)
        
        db.session.commit()
        flash('Sample data initialized successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error initializing data: {str(e)}', 'error')
    
    return redirect(url_for('index'))
