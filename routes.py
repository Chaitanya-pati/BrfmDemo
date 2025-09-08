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
    """Main dashboard - production functionality removed"""
    # Dashboard data without production references
    pending_vehicles = Vehicle.query.filter_by(status='pending').count()
    quality_check_vehicles = Vehicle.query.filter_by(status='quality_check').count()
    pending_dispatches = Dispatch.query.filter_by(status='loaded').count()
    
    # Recent activities
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    
    return render_template('index.html', 
                         pending_vehicles=pending_vehicles,
                         quality_check_vehicles=quality_check_vehicles,
                         active_orders=0,  # Production orders removed
                         pending_dispatches=pending_dispatches,
                         recent_vehicles=recent_vehicles,
                         recent_orders=[])  # Production orders removed

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
                product.price_per_kg = float(request.form.get('price_per_kg', 0))
                db.session.add(product)
            
            db.session.commit()
            flash(f'{form_type.title()} added successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding {form_type}: {str(e)}', 'error')
    
    suppliers = Supplier.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    godown_types = GodownType.query.all()
    
    return render_template('masters.html', suppliers=suppliers, customers=customers, 
                         products=products, godown_types=godown_types)

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
            order.responsible_person = request.form.get('responsible_person', 'Production Manager')
            
            db.session.add(order)
            db.session.commit()
            
            # Send notification to responsible person
            notify_responsible_person(
                order.order_number,
                order.responsible_person,
                order.finished_good_type,
                order.quantity
            )
            
            # Mark notification as sent
            order.notification_sent = True
            db.session.commit()
            
            flash(f'Production Order {order.order_number} created successfully! Notification sent to {order.responsible_person}.', 'success')
            return redirect(url_for('production_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production order: {str(e)}', 'error')
    
    # Get all production orders
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    
    return render_template('production_orders.html', orders=orders)

@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id):
    """Handle production planning with bin percentages"""
    order = ProductionOrder.query.get_or_404(order_id)
    
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
                    order_id=order_id,
                    created_by=request.form.get('created_by', 'Production Manager')
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
            order.planned_at = datetime.now()
            
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