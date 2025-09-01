import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from app import app, db
from models import (Vehicle, Supplier, Godown, GodownType, QualityTest, Transfer, 
                   PrecleaningBin, ProductionOrder, ProductionPlan, ProductionPlanItem, ProductionJobNew,
                   Customer, Product, SalesDispatch, CleaningProcess, CleaningMachine, CleaningBin,
                   ProductionTransfer, GrindingProcess, ProductOutput, PackingProcess,
                   CleaningLog, StorageArea, StorageTransfer, MachineCleaningLog, CleaningSchedule)
from utils import allowed_file, generate_order_number
import random
import string

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
            production_order.finished_good_type = request.form['finished_good_type']
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






# Legacy route - replaced by production_tracking

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

# Production Execution System with Timer Controls
@app.route('/production_execution')
def production_execution():
    # Get running processes for alerts
    try:
        running_processes = CleaningProcess.query.filter_by(status='running').all()
    except Exception as e:
        # Handle missing column error gracefully
        print(f"Database column error: {e}")
        # Reset any database transaction issues
        db.session.rollback()
        running_processes = []

    return render_template('production_execution.html', 
                         running_processes=running_processes)

def generate_job_id():
    """Generate unique job ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"JOB{timestamp}{random_suffix}"

@app.route('/start_production_process/<int:order_id>')
def start_production_process(order_id):
    """Prepare to start production - doesn't create jobs until actual execution begins"""
    try:
        order = ProductionOrder.query.get_or_404(order_id)
        plan = ProductionPlan.query.filter_by(order_id=order_id, status='approved').first()

        if not plan:
            flash('No approved production plan found for this order', 'error')
            return redirect(url_for('production_orders'))

        # Check if execution already started
        existing_job = ProductionJobNew.query.filter_by(order_id=order_id).first()
        if existing_job:
            flash('Production already started for this order', 'warning')
            return redirect(url_for('production_execution'))

        # Don't create jobs yet - just redirect to transfer execution setup
        return redirect(url_for('transfer_execution_setup', order_id=order_id))

    except Exception as e:
        flash(f'Error preparing production: {str(e)}', 'error')
        return redirect(url_for('production_orders'))

@app.route('/production_execution/transfer_setup/<int:order_id>', methods=['GET', 'POST'])
def transfer_execution_setup(order_id):
    """Setup and begin transfer execution - creates job only when actually started"""
    order = ProductionOrder.query.get_or_404(order_id)
    plan = ProductionPlan.query.filter_by(order_id=order_id, status='approved').first()

    if not plan:
        flash('No approved production plan found for this order', 'error')
        return redirect(url_for('production_orders'))

    # Check if execution already started
    existing_job = ProductionJobNew.query.filter_by(order_id=order_id).first()
    if existing_job:
        flash('Production already started for this order', 'warning')
        return redirect(url_for('production_execution'))

    plan_items = ProductionPlanItem.query.filter_by(plan_id=plan.id).all()
    
    # Get only the precleaning bins that are in the plan and have sufficient stock
    valid_plan_items = []
    for item in plan_items:
        precleaning_bin = PrecleaningBin.query.get(item.precleaning_bin_id)
        if precleaning_bin and precleaning_bin.current_stock >= item.quantity:
            valid_plan_items.append(item)

    if request.method == 'POST':
        try:
            # Check if all plan items have sufficient stock
            for item in plan_items:
                precleaning_bin = PrecleaningBin.query.get(item.precleaning_bin_id)
                if not precleaning_bin or precleaning_bin.current_stock < item.quantity:
                    flash(f'Insufficient stock in {precleaning_bin.name if precleaning_bin else "Unknown bin"}', 'error')
                    return redirect(url_for('transfer_execution_setup', order_id=order_id))

            # NOW create the job since user is actually starting execution
            job = ProductionJobNew()
            job.job_number = generate_job_id()
            job.order_id = order_id
            job.plan_id = plan.id
            job.stage = 'transfer'
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            job.started_by = request.form['operator_name']

            # Update order status to in_progress
            order.status = 'in_progress'

            db.session.add(job)
            db.session.flush()  # Get job ID

            total_transferred = 0

            # Process each precleaning bin transfer automatically
            for plan_item in plan_items:
                quantity_to_transfer = plan_item.quantity

                # Create transfer record
                transfer = ProductionTransfer()
                transfer.job_id = job.id
                transfer.from_precleaning_bin_id = plan_item.precleaning_bin_id
                transfer.quantity_transferred = quantity_to_transfer
                transfer.operator_name = request.form['operator_name']

                # Handle photos
                if 'start_photo' in request.files:
                    file = request.files['start_photo']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filename = f"transfer_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        transfer.start_photo = filename

                # Update precleaning bin stock
                precleaning_bin = PrecleaningBin.query.get(plan_item.precleaning_bin_id)
                if precleaning_bin:
                    precleaning_bin.current_stock -= quantity_to_transfer

                total_transferred += quantity_to_transfer
                db.session.add(transfer)

            # Complete transfer job
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = request.form['operator_name']

            # Create cleaning_24h job
            cleaning_job = ProductionJobNew()
            cleaning_job.job_number = generate_job_id()
            cleaning_job.order_id = job.order_id
            cleaning_job.plan_id = job.plan_id
            cleaning_job.stage = 'cleaning_24h'
            cleaning_job.status = 'pending'

            db.session.add(cleaning_job)
            db.session.commit()

            flash(f'Production started! Transfer completed: {total_transferred:.2f} kg', 'success')
            return redirect(url_for('cleaning_setup', job_id=cleaning_job.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error starting production: {str(e)}', 'error')

    return render_template('transfer_execution_setup.html', 
                         order=order,
                         plan=plan,
                         plan_items=valid_plan_items)

@app.route('/production_execution/transfer/<int:job_id>', methods=['GET', 'POST'])
def transfer_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    plan_items = ProductionPlanItem.query.filter_by(plan_id=job.plan_id).all()

    # Get only the precleaning bins that are in the plan and have sufficient stock
    valid_plan_items = []
    for item in plan_items:
        precleaning_bin = PrecleaningBin.query.get(item.precleaning_bin_id)
        if precleaning_bin and precleaning_bin.current_stock >= item.quantity:
            valid_plan_items.append(item)

    if request.method == 'POST':
        try:
            # Check if all plan items have sufficient stock
            for item in plan_items:
                precleaning_bin = PrecleaningBin.query.get(item.precleaning_bin_id)
                if not precleaning_bin or precleaning_bin.current_stock < item.quantity:
                    flash(f'Insufficient stock in {precleaning_bin.name if precleaning_bin else "Unknown bin"}', 'error')
                    return redirect(url_for('transfer_execution', job_id=job_id))

            # Mark job as started
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            job.started_by = request.form['operator_name']

            total_transferred = 0

            # Process each precleaning bin transfer automatically
            for plan_item in plan_items:
                quantity_to_transfer = plan_item.quantity

                # Create transfer record
                transfer = ProductionTransfer()
                transfer.job_id = job_id
                transfer.from_precleaning_bin_id = plan_item.precleaning_bin_id
                transfer.quantity_transferred = quantity_to_transfer
                transfer.operator_name = request.form['operator_name']

                # Handle photos
                if 'start_photo' in request.files:
                    file = request.files['start_photo']
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filename = f"transfer_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        transfer.start_photo = filename

                # Update precleaning bin stock
                precleaning_bin = PrecleaningBin.query.get(plan_item.precleaning_bin_id)
                if precleaning_bin:
                    precleaning_bin.current_stock -= quantity_to_transfer

                total_transferred += quantity_to_transfer
                db.session.add(transfer)

            # Complete transfer job
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = request.form['operator_name']

            # Create cleaning_24h job
            cleaning_job = ProductionJobNew()
            cleaning_job.job_number = generate_job_id()
            cleaning_job.order_id = job.order_id
            cleaning_job.plan_id = job.plan_id
            cleaning_job.stage = 'cleaning_24h'
            cleaning_job.status = 'pending'

            db.session.add(cleaning_job)
            db.session.commit()

            flash(f'Transfer completed successfully! Total transferred: {total_transferred:.2f} kg', 'success')
            return redirect(url_for('cleaning_setup', job_id=cleaning_job.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error during transfer: {str(e)}', 'error')

    return render_template('transfer_execution.html', 
                         job=job, 
                         plan_items=valid_plan_items)

@app.route('/production_execution/cleaning_setup/<int:job_id>', methods=['GET', 'POST'])
def cleaning_setup(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    cleaning_bins = CleaningBin.query.filter_by(status='empty').all()

    if request.method == 'POST':
        try:
            duration_option = request.form['duration_option']
            duration_hours = 24  # default

            if duration_option == '24':
                duration_hours = 24
            elif duration_option == '12':
                duration_hours = 12
            elif duration_option == 'custom':
                duration_hours = float(request.form['custom_hours'])

            # Create cleaning process
            cleaning = CleaningProcess()
            cleaning.job_id = job_id
            cleaning.process_type = f"{duration_hours}_hour_cleaning"
            cleaning.cleaning_bin_id = int(request.form['cleaning_bin_id'])
            cleaning.duration_hours = duration_hours
            cleaning.start_time = datetime.utcnow()
            cleaning.end_time = datetime.utcnow() + timedelta(hours=duration_hours)
            cleaning.machine_name = request.form['machine_name']
            cleaning.operator_name = request.form['operator_name']
            cleaning.start_moisture = float(request.form.get('start_moisture', 0))
            cleaning.status = 'running'

            # Update cleaning bin status (create if doesn't exist for hardcoded option)
            cleaning_bin = CleaningBin.query.get(cleaning.cleaning_bin_id)
            if not cleaning_bin and cleaning.cleaning_bin_id == 1:
                # Create default cleaning bin if it doesn't exist
                cleaning_bin = CleaningBin(
                    id=1,
                    name='Cleaning Bin #1',
                    capacity=100.0,
                    status='cleaning',
                    cleaning_type='24_hour'
                )
                db.session.add(cleaning_bin)
            elif cleaning_bin:
                cleaning_bin.status = 'cleaning'


            # Update job
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            job.started_by = request.form['operator_name']

            db.session.add(cleaning)
            db.session.commit()

            flash(f'Cleaning process started! Duration: {duration_hours} hours', 'success')
            return redirect(url_for('cleaning_monitor', process_id=cleaning.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error starting cleaning process: {str(e)}', 'error')

    return render_template('cleaning_setup.html', job=job, cleaning_bins=cleaning_bins)

@app.route('/production_execution/cleaning_monitor/<int:process_id>')
def cleaning_monitor(process_id):
    from models import CleaningSchedule, ProductionMachine, MachineCleaningLog
    
    process = CleaningProcess.query.get_or_404(process_id)

    # Calculate remaining time
    now = datetime.utcnow()
    time_remaining = (process.end_time - now).total_seconds()

    # Check if reminder should be shown (1 hour before completion)
    show_reminder = False
    if time_remaining > 0 and time_remaining <= 3600:  # 1 hour = 3600 seconds
        show_reminder = True

    if time_remaining <= 0:
        time_remaining = 0
        if process.status == 'running':
            process.status = 'completed'
            # Update cleaning bin status
            cleaning_bin = CleaningBin.query.get(process.cleaning_bin_id)
            if cleaning_bin:
                cleaning_bin.status = 'empty'
            db.session.commit()

    # Get machine cleaning schedules for this process
    job_id = process.job_id
    
    # Get the job to find the correct process step
    job = ProductionJobNew.query.get(job_id)
    process_step = job.stage if job else None
    
    # Find active machines for this process step
    active_machines = ProductionMachine.query.filter_by(process_step=process_step, is_active=True).all()
    print(f"DEBUG: Process type: {process.process_type}, Job stage: {process_step}, Active machines: {len(active_machines)}")
    
    # Get scheduled machine cleanings that are due
    scheduled_cleanings = CleaningSchedule.query.filter(
        CleaningSchedule.job_id == job_id,
        CleaningSchedule.status == 'scheduled',
        CleaningSchedule.scheduled_time <= now + timedelta(minutes=1)  # Due within 1 minute
    ).all()
    
    # Get in-progress machine cleanings
    in_progress_cleanings = MachineCleaningLog.query.filter_by(
        job_id=job_id,
        status='in_progress'
    ).all()
    
    # Calculate machine cleaning timers
    machine_cleaning_timers = []
    for cleaning in in_progress_cleanings:
        if cleaning.cleaning_start_time:
            elapsed_time = (now - cleaning.cleaning_start_time).total_seconds()
            machine_cleaning_timers.append({
                'log': cleaning,
                'elapsed_time': elapsed_time
            })

    return render_template('cleaning_monitor.html', 
                         process=process, 
                         time_remaining=time_remaining,
                         show_reminder=show_reminder,
                         scheduled_cleanings=scheduled_cleanings,
                         in_progress_cleanings=in_progress_cleanings,
                         machine_cleaning_timers=machine_cleaning_timers,
                         active_machines=active_machines)

@app.route('/production_execution/complete_cleaning/<int:process_id>', methods=['GET', 'POST'])
def complete_cleaning(process_id):
    process = CleaningProcess.query.get_or_404(process_id)

    # Check if timer is completed
    now = datetime.utcnow()
    if now < process.end_time:
        flash('Cannot complete cleaning process until timer finishes!', 'error')
        return redirect(url_for('cleaning_monitor', process_id=process_id))

    if request.method == 'POST':
        try:
            # Update cleaning process with completion data
            process.actual_end_time = datetime.utcnow()
            process.end_moisture = float(request.form['end_moisture'])
            process.waste_collected_kg = float(request.form['waste_collected'])
            process.water_added_liters = float(request.form['water_added'])
            process.completed_by = request.form['completed_by']
            process.notes = request.form.get('notes', '')
            process.status = 'completed'

            # Handle end photo
            if 'end_photo' in request.files:
                file = request.files['end_photo']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"cleaning_end_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    process.end_photo = filename

            # Update cleaning bin status
            cleaning_bin = CleaningBin.query.get(process.cleaning_bin_id)
            if cleaning_bin:
                cleaning_bin.status = 'empty'

            # Complete the job
            job = ProductionJobNew.query.get(process.job_id)
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = request.form['completed_by']

            # Enhanced workflow transition logic
            if job.stage == 'cleaning_24h' or 'hour_cleaning' in process.process_type:
                # Check if this is the first cleaning (24h) - create 12h job
                if '24' in process.process_type or job.stage == 'cleaning_24h':
                    cleaning_12h_job = ProductionJobNew()
                    cleaning_12h_job.job_number = generate_job_id()
                    cleaning_12h_job.order_id = job.order_id
                    cleaning_12h_job.plan_id = job.plan_id
                    cleaning_12h_job.stage = 'cleaning_12h'
                    cleaning_12h_job.status = 'pending'
                    process.next_process_job_id = cleaning_12h_job.id
                    db.session.add(cleaning_12h_job)

                    db.session.commit()
                    flash('24-hour cleaning completed! Ready for 12-hour cleaning process.', 'success')
                    return redirect(url_for('cleaning_12h_setup', job_id=cleaning_12h_job.id))
                elif job.stage == 'cleaning_12h' or '12h' in process.process_type:
                    # 12h cleaning completed - move to grinding with B1 scale
                    grinding_job = ProductionJobNew()
                    grinding_job.job_number = generate_job_id()
                    grinding_job.order_id = job.order_id
                    grinding_job.plan_id = job.plan_id
                    grinding_job.stage = 'grinding'
                    grinding_job.status = 'pending'
                    db.session.add(grinding_job)

                    db.session.commit()
                    flash('12-hour cleaning completed! Ready for B1 scale and grinding process.', 'success')
                    return redirect(url_for('b1_scale_process', job_id=grinding_job.id))
            else:
                db.session.commit()
                flash('Cleaning process completed successfully!', 'success')
                return redirect(url_for('production_execution'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error completing cleaning process: {str(e)}', 'error')

    return render_template('complete_cleaning.html', log=process)

# 12-Hour Cleaning Setup Route
@app.route('/production_execution/cleaning_12h_setup/<int:job_id>', methods=['GET', 'POST'])
def cleaning_12h_setup(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    cleaning_bins_12h = CleaningBin.query.filter_by(status='empty', cleaning_type='12_hour').all()

    if request.method == 'POST':
        try:
            duration_option = request.form['duration_option']
            duration_hours = 12  # default

            if duration_option == '24':
                duration_hours = 24
            elif duration_option == '12':
                duration_hours = 12
            elif duration_option == 'custom':
                duration_hours = float(request.form['custom_hours'])

            # Create 12-hour cleaning process
            cleaning = CleaningProcess()
            cleaning.job_id = job_id
            cleaning.process_type = f"{duration_hours}_hour_cleaning_12h"
            cleaning.cleaning_bin_id = int(request.form['cleaning_bin_id'])
            cleaning.duration_hours = duration_hours
            cleaning.start_time = datetime.utcnow()
            cleaning.end_time = datetime.utcnow() + timedelta(hours=duration_hours)
            cleaning.machine_name = request.form['machine_name']
            cleaning.operator_name = request.form['operator_name']
            cleaning.start_moisture = float(request.form.get('start_moisture', 0))
            cleaning.target_moisture = float(request.form.get('target_moisture', 0))
            cleaning.status = 'running'

            # Update cleaning bin status (create if doesn't exist for hardcoded option)
            cleaning_bin = CleaningBin.query.get(cleaning.cleaning_bin_id)
            if not cleaning_bin and cleaning.cleaning_bin_id == 2:
                # Create default 12-hour cleaning bin if it doesn't exist
                cleaning_bin = CleaningBin(
                    id=2,
                    name='12-Hour Cleaning Bin #1',
                    capacity=100.0,
                    status='cleaning',
                    cleaning_type='12_hour'
                )
                db.session.add(cleaning_bin)
            elif cleaning_bin:
                cleaning_bin.status = 'cleaning'

            # Update job
            job.status = 'in_progress'
            job.started_at = datetime.utcnow()
            job.started_by = request.form['operator_name']

            db.session.add(cleaning)
            db.session.commit()

            flash(f'12-hour cleaning process started! Duration: {duration_hours} hours', 'success')
            return redirect(url_for('cleaning_monitor', process_id=cleaning.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error starting 12-hour cleaning process: {str(e)}', 'error')

    return render_template('cleaning_12h_setup.html', job=job, cleaning_bins=cleaning_bins_12h)

@app.route('/production_tracking')
def production_tracking():
    # Get all orders with their plans and jobs
    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()

    # Get orders with plans
    planned_orders = []
    for order in orders:
        plan = ProductionPlan.query.filter_by(order_id=order.id).first()
        jobs = ProductionJobNew.query.filter_by(order_id=order.id).all()

        order_data = {
            'order': order,
            'plan': plan,
            'jobs': jobs,
            'job_count': len(jobs),
            'completed_jobs': len([j for j in jobs if j.status == 'completed']),
            'progress_percentage': (len([j for j in jobs if j.status == 'completed']) / len(jobs) * 100) if jobs else 0
        }
        planned_orders.append(order_data)

    return render_template('production_tracking.html', planned_orders=planned_orders)

@app.route('/order_tracking/<order_number>')
def order_tracking_detail(order_number):
    """Display detailed tracking for a specific order"""
    order = ProductionOrder.query.filter_by(order_number=order_number).first_or_404()
    plan = ProductionPlan.query.filter_by(order_id=order.id).first()
    jobs = ProductionJobNew.query.filter_by(order_id=order.id).order_by(ProductionJobNew.created_at).all()

    # Build job details with associated processes
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
            'grinding_processes': GrindingProcess.query.filter_by(job_id=job.id).all() if hasattr(job, 'grinding_processes') else [],
            'machine_cleanings': machine_cleanings,
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

@app.route('/api/order_tracking/<order_number>')
def api_order_tracking(order_number):
    """API endpoint to get complete order lifecycle data"""
    order = ProductionOrder.query.filter_by(order_number=order_number).first()

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Get production plan
    plan = ProductionPlan.query.filter_by(order_id=order.id).first()

    # Get all jobs
    jobs = ProductionJobNew.query.filter_by(order_id=order.id).order_by(ProductionJobNew.created_at).all()

    # Get all transfers
    transfers = []
    for job in jobs:
        job_transfers = ProductionTransfer.query.filter_by(job_id=job.id).all()
        transfers.extend(job_transfers)

    # Get all cleaning processes
    cleaning_processes = []
    machine_cleanings = []
    for job in jobs:
        job_cleanings = CleaningProcess.query.filter_by(job_id=job.id).all()
        job_machine_cleanings = MachineCleaningLog.query.filter_by(job_id=job.id).all()
        cleaning_processes.extend(job_cleanings)
        machine_cleanings.extend(job_machine_cleanings)

    # Build response
    tracking_data = {
        'order': {
            'id': order.id,
            'order_number': order.order_number,
            'customer': order.customer,
            'quantity': order.quantity,
            'product': order.product,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'deadline': order.deadline.isoformat() if order.deadline else None
        },
        'plan': {
            'id': plan.id,
            'planned_by': plan.planned_by,
            'planning_date': plan.planning_date.isoformat() if plan.planning_date else None,
            'status': plan.status,
            'total_percentage': plan.total_percentage
        } if plan else None,
        'jobs': [{
            'id': job.id,
            'job_number': job.job_number,
            'stage': job.stage,
            'status': job.status,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'started_by': job.started_by,
            'completed_by': job.completed_by
        } for job in jobs],
        'transfers': [{
            'id': transfer.id,
            'from_bin': transfer.from_bin.name if transfer.from_bin else 'Unknown',
            'quantity_transferred': transfer.quantity_transferred,
            'transfer_time': transfer.transfer_time.isoformat() if transfer.transfer_time else None,
            'operator_name': transfer.operator_name
        } for transfer in transfers],
        'cleaning_processes': [{
            'id': cleaning.id,
            'process_type': cleaning.process_type,
            'duration_hours': cleaning.duration_hours,
            'machine_name': cleaning.machine_name,
            'start_time': cleaning.start_time.isoformat() if cleaning.start_time else None,
            'end_time': cleaning.end_time.isoformat() if cleaning.end_time else None,
            'actual_end_time': cleaning.actual_end_time.isoformat() if cleaning.actual_end_time else None,
            'start_moisture': cleaning.start_moisture,
            'end_moisture': cleaning.end_moisture,
            'water_added_liters': cleaning.water_added_liters,
            'waste_collected_kg': cleaning.waste_collected_kg,
            'status': cleaning.status,
            'operator_name': cleaning.operator_name,
            'completed_by': cleaning.completed_by
        } for cleaning in cleaning_processes],
        'machine_cleanings': [{
            'id': mc.id,
            'machine_name': mc.machine.name,
            'machine_location': mc.machine.location,
            'process_step': mc.process_step,
            'cleaned_by': mc.cleaned_by,
            'cleaning_start_time': mc.cleaning_start_time.isoformat() if mc.cleaning_start_time else None,
            'cleaning_end_time': mc.cleaning_end_time.isoformat() if mc.cleaning_end_time else None,
            'cleaning_duration_minutes': mc.cleaning_duration_minutes,
            'waste_collected_kg': mc.waste_collected_kg,
            'status': mc.status,
            'has_before_photo': bool(mc.photo_before),
            'has_after_photo': bool(mc.photo_after),
            'notes': mc.notes
        } for mc in machine_cleanings]
    }

    return jsonify(tracking_data)

@app.route('/api/cleaning_timer/<int:process_id>')
def api_cleaning_timer(process_id):
    """API endpoint for real-time timer updates"""
    process = CleaningProcess.query.get_or_404(process_id)

    now = datetime.utcnow()
    time_remaining = (process.end_time - now).total_seconds()

    # Check if reminder should be shown (1 hour before completion for 12h process)
    show_reminder = False
    if '12h' in process.process_type and time_remaining > 0 and time_remaining <= 3600:
        show_reminder = True

    return jsonify({
        'time_remaining': max(0, time_remaining),
        'status': process.status,
        'can_complete': time_remaining <= 0 and process.status == 'running',
        'show_reminder': show_reminder,
        'process_type': process.process_type
    })

@app.route('/sales_dispatch', methods=['GET', 'POST'])
def sales_dispatch():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_order':
            try:
                # Import SalesOrder model
                from models import SalesOrder

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

        elif action == 'dispatch':
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

                # Import required models
                from models import Dispatch, SalesOrder, DispatchVehicle

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

                # Update vehicle status to dispatched
                vehicle = DispatchVehicle.query.get(request.form['vehicle_id'])
                if vehicle:
                    vehicle.status = 'dispatched'

                db.session.add(dispatch)
                db.session.commit()
                flash('Dispatch created successfully!', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating dispatch: {str(e)}', 'error')

        else:
            # Fallback for old dispatch creation without action
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

    # Import models for template data
    from models import SalesOrder, DispatchVehicle, Dispatch

    completed_orders = ProductionOrder.query.filter_by(status='completed').all()
    customers = Customer.query.all()
    products = Product.query.all()
    dispatches = SalesDispatch.query.order_by(SalesDispatch.created_at.desc()).limit(20).all()

    # Get sales orders and vehicles for the new functionality
    sales_orders = SalesOrder.query.filter(SalesOrder.status.in_(['pending', 'partial'])).all()
    vehicles = DispatchVehicle.query.filter_by(status='available').all()
    dispatches = Dispatch.query.order_by(Dispatch.dispatch_date.desc()).limit(10).all()

    return render_template('sales_dispatch.html', 
                         orders=completed_orders, 
                         customers=customers, 
                         products=products, 
                         dispatches=dispatches,
                         sales_orders=sales_orders,
                         vehicles=vehicles)

# B1 Scale Process - Step between 12h cleaning and grinding
@app.route('/production_execution/b1_scale/<int:job_id>', methods=['GET', 'POST'])
def b1_scale_process(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)
    
    # Check if B1 scale machine needs cleaning (every hour)
    from models import B1ScaleCleaning
    b1_machine = B1ScaleCleaning.query.first()
    if not b1_machine:
        # Create B1 scale machine if it doesn't exist
        b1_machine = B1ScaleCleaning(
            machine_name='B1 Scale',
            cleaning_frequency_minutes=60,
            last_cleaned=datetime.utcnow(),
            next_cleaning_due=datetime.utcnow() + timedelta(minutes=60),
            status='due'
        )
        db.session.add(b1_machine)
        db.session.commit()
    
    # Check if cleaning is due (within 10 minutes)
    time_until_cleaning = (b1_machine.next_cleaning_due - datetime.utcnow()).total_seconds() / 60
    cleaning_required = time_until_cleaning <= 10
    cleaning_urgent = time_until_cleaning <= 5
    
    if request.method == 'POST':
        if request.form.get('action') == 'proceed_to_grinding':
            # Proceed to grinding if no cleaning required or cleaning completed
            if cleaning_required and b1_machine.status != 'completed':
                flash('B1 Scale cleaning is required before proceeding to grinding!', 'error')
                return redirect(url_for('b1_scale_process', job_id=job_id))
            
            return redirect(url_for('grinding_execution', job_id=job_id))
    
    return render_template('b1_scale_process.html', 
                         job=job, 
                         b1_machine=b1_machine,
                         cleaning_required=cleaning_required,
                         cleaning_urgent=cleaning_urgent,
                         time_until_cleaning=time_until_cleaning)

@app.route('/production_execution/b1_scale_cleaning/<int:job_id>', methods=['GET', 'POST'])
def b1_scale_cleaning(job_id):
    from models import B1ScaleCleaning, B1ScaleCleaningLog
    job = ProductionJobNew.query.get_or_404(job_id)
    b1_machine = B1ScaleCleaning.query.first()
    
    if request.method == 'POST':
        try:
            # Handle file uploads
            before_photo = None
            after_photo = None

            if 'before_cleaning_photo' in request.files:
                file = request.files['before_cleaning_photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"b1_before_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    before_photo = filename

            if 'after_cleaning_photo' in request.files:
                file = request.files['after_cleaning_photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"b1_after_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    after_photo = filename

            # Create cleaning log
            cleaning_log = B1ScaleCleaningLog(
                machine_id=b1_machine.id,
                cleaned_by=request.form['cleaned_by'],
                cleaning_start_time=datetime.utcnow(),
                cleaning_end_time=datetime.utcnow(),
                before_cleaning_photo=before_photo,
                after_cleaning_photo=after_photo,
                waste_collected_kg=float(request.form.get('waste_collected', 0)),
                notes=request.form.get('notes', ''),
                status='completed'
            )

            # Update machine status
            b1_machine.last_cleaned = datetime.utcnow()
            b1_machine.next_cleaning_due = datetime.utcnow() + timedelta(minutes=b1_machine.cleaning_frequency_minutes)
            b1_machine.status = 'completed'

            db.session.add(cleaning_log)
            db.session.commit()

            flash('B1 Scale cleaning completed successfully!', 'success')
            return redirect(url_for('b1_scale_process', job_id=job_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error completing B1 scale cleaning: {str(e)}', 'error')

    return render_template('b1_scale_cleaning.html', job=job, b1_machine=b1_machine)

# Step 3: Grinding Process with Machine Cleaning
@app.route('/production_execution/grinding/<int:job_id>', methods=['GET', 'POST'])
def grinding_execution(job_id):
    job = ProductionJobNew.query.get_or_404(job_id)

    # Check if grinding process already exists with error handling
    existing_grinding = None
    try:
        existing_grinding = GrindingProcess.query.filter_by(job_id=job_id).first()
    except Exception as e:
        print(f"Error querying grinding process: {e}")
        db.session.rollback()

    if request.method == 'POST':
        try:
            if existing_grinding:
                flash('Grinding process already exists for this job!', 'error')
                return redirect(url_for('grinding_execution', job_id=job_id))

            # Handle file uploads
            start_photo = None
            end_photo = None

            if 'start_photo' in request.files:
                file = request.files['start_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"grinding_start_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    start_photo = filename

            if 'end_photo' in request.files:
                file = request.files['end_photo']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"grinding_end_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    end_photo = filename

            # Create grinding process
            grinding = GrindingProcess()
            grinding.job_id = job_id
            grinding.machine_name = request.form['machine_name']
            grinding.operator_name = request.form['operator_name']
            grinding.input_quantity_kg = float(request.form['input_quantity'])
            grinding.main_products_kg = float(request.form['main_products'])
            grinding.bran_kg = float(request.form['bran'])
            grinding.total_output_kg = grinding.main_products_kg + grinding.bran_kg
            grinding.bran_percentage = (grinding.bran_kg / grinding.total_output_kg) * 100 if grinding.total_output_kg > 0 else 0
            grinding.start_time = datetime.utcnow()
            grinding.end_time = datetime.utcnow()
            grinding.start_photo = start_photo
            grinding.end_photo = end_photo
            grinding.status = 'completed'

            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.completed_by = request.form['operator_name']

            # Enhanced bran percentage validation and alerts
            grinding.main_products_percentage = (grinding.main_products_kg / grinding.total_output_kg) * 100 if grinding.total_output_kg > 0 else 0
            grinding.bran_percentage_alert = grinding.bran_percentage > 25
            
            # B1 Scale integration
            grinding.b1_scale_operator = request.form.get('b1_scale_operator', '')
            grinding.b1_scale_start_time = datetime.utcnow()
            grinding.b1_scale_weight_kg = float(request.form.get('b1_scale_weight', grinding.input_quantity_kg))
            
            # Check bran percentage and create alert if needed
            if grinding.bran_percentage > 25:
                grinding.bran_percentage_alert = True
                flash(f'⚠️ ALERT: Bran percentage ({grinding.bran_percentage:.1f}%) is higher than expected range (23-25%)', 'warning')
            elif grinding.bran_percentage < 23:
                grinding.bran_percentage_alert = True
                flash(f'⚠️ ALERT: Bran percentage ({grinding.bran_percentage:.1f}%) is lower than expected range (23-25%)', 'warning')
            else:
                flash(f'✅ Bran percentage ({grinding.bran_percentage:.1f}%) is within expected range (23-25%)', 'success')

            db.session.add(grinding)
            db.session.commit()

            flash('Grinding process completed successfully!', 'success')
            return redirect(url_for('packing_execution', job_id=job_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error completing grinding process: {str(e)}', 'error')

    return render_template('grinding_execution.html', job=job, existing_grinding=existing_grinding)

# Machine Cleaning with Hourly Frequency
@app.route('/machine_cleaning', methods=['GET', 'POST'])
def machine_cleaning():
    if request.method == 'POST':
        try:
            action = request.form.get('action')

            if action == 'start_cleaning':
                machine_id = int(request.form['machine_id'])
                operator = request.form['operator']

                # Check if machine needs cleaning
                machine = CleaningMachine.query.get(machine_id)
                if not machine:
                    flash('Machine not found!', 'error')
                    return redirect(url_for('machine_cleaning'))

                # Handle photo upload
                before_photo = None
                if 'before_photo' in request.files:
                    file = request.files['before_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"before_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        before_photo = filename

                # Create cleaning log
                log = CleaningLog()
                log.machine_id = machine_id
                log.cleaned_by = operator
                log.photo_before = before_photo
                log.waste_collected = float(request.form.get('waste_collected', 0))
                log.notes = request.form.get('notes', '')

                # Update machine last cleaned time
                machine.last_cleaned = datetime.utcnow()

                db.session.add(log)
                db.session.commit()

                flash('Machine cleaning started!', 'success')
                return redirect(url_for('complete_machine_cleaning', log_id=log.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error starting machine cleaning: {str(e)}', 'error')

    # Get machines that need cleaning (every hour)
    now = datetime.utcnow()
    machines_needing_cleaning = CleaningMachine.query.filter(
        db.or_(
            CleaningMachine.last_cleaned.is_(None),
            CleaningMachine.last_cleaned <= now - timedelta(hours=1)
        )
    ).all()

    all_machines = CleaningMachine.query.all()
    recent_logs = CleaningLog.query.order_by(CleaningLog.cleaning_time.desc()).limit(10).all()

    return render_template('machine_cleaning.html', 
                         machines_needing_cleaning=machines_needing_cleaning,
                         all_machines=all_machines,
                         recent_logs=recent_logs)

@app.route('/complete_machine_cleaning/<int:log_id>', methods=['GET', 'POST'])
def complete_machine_cleaning(log_id):
    log = CleaningLog.query.get_or_404(log_id)

    if request.method == 'POST':
        try:
            # Handle after photo upload
            after_photo = None
            if 'after_photo' in request.files:
                file = request.files['after_photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"after_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    after_photo = filename

            log.photo_after = after_photo
            log.waste_collected = float(request.form.get('waste_collected', log.waste_collected or 0))
            log.notes = request.form.get('notes', log.notes or '')

            db.session.commit()
            flash('Machine cleaning completed successfully!', 'success')
            return redirect(url_for('machine_cleaning'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error completing machine cleaning: {str(e)}', 'error')

    return render_template('complete_cleaning.html', log=log)

# Step 4: Packing Process
@app.route('/production_execution/packing/<int:job_id>', methods=['GET', 'POST'])
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
            action = request.form.get('action')

            if action == 'pack_product':
                product_id = int(request.form['product_id'])
                bag_weight = float(request.form['bag_weight'])
                number_of_bags = int(request.form['number_of_bags'])
                storage_area_id = request.form.get('storage_area_id')
                stored_in_shallow = float(request.form.get('stored_in_shallow', 0))
                operator = request.form['operator_name']

                # Handle photo upload
                packing_photo = None
                if 'packing_photo' in request.files:
                    file = request.files['packing_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"packing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        packing_photo = filename

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
                db.session.commit()

                flash(f'Packed {number_of_bags} bags of {bag_weight}kg each successfully!', 'success')

            elif action == 'complete_packing':
                operator = request.form['operator_name']
                
                # Handle photo upload
                packing_photo = None
                if 'packing_photo' in request.files:
                    file = request.files['packing_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"packing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
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
                        total_packed_count += 1
                
                # Mark job as completed
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
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

    return render_template('packing_execution.html', 
                         job=job, 
                         grinding_process=grinding_process,
                         products=products,
                         storage_areas=storage_areas,
                         existing_packing=existing_packing)

# Storage Management
@app.route('/storage_management', methods=['GET', 'POST'])
def storage_management():
    if request.method == 'POST':
        try:
            action = request.form.get('action')

            if action == 'transfer_storage':
                from_storage_id = int(request.form['from_storage_id'])
                to_storage_id = int(request.form['to_storage_id'])
                product_id = int(request.form['product_id'])
                quantity = float(request.form['quantity'])
                operator = request.form['operator_name']
                reason = request.form.get('reason', '')

                # Validate transfer
                from_storage = StorageArea.query.get(from_storage_id)
                to_storage = StorageArea.query.get(to_storage_id)

                if not from_storage or not to_storage:
                    flash('Invalid storage areas selected!', 'error')
                    return redirect(url_for('storage_management'))

                if from_storage.current_stock_kg < quantity:
                    flash('Insufficient stock in source storage area!', 'error')
                    return redirect(url_for('storage_management'))

                if to_storage.current_stock_kg + quantity > to_storage.capacity_kg:
                    flash('Destination storage area does not have enough capacity!', 'warning')

                # Create transfer record
                transfer = StorageTransfer()
                transfer.from_storage_id = from_storage_id
                transfer.to_storage_id = to_storage_id
                transfer.product_id = product_id
                transfer.quantity_kg = quantity
                transfer.operator_name = operator
                transfer.reason = reason

                # Update storage stocks
                from_storage.current_stock_kg -= quantity
                to_storage.current_stock_kg += quantity

                db.session.add(transfer)
                db.session.commit()

                flash(f'Transfer of {quantity}kg completed successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error in storage transfer: {str(e)}', 'error')

    storage_areas = StorageArea.query.all()
    products = Product.query.all()
    recent_transfers = StorageTransfer.query.order_by(StorageTransfer.transfer_time.desc()).limit(10).all()

    return render_template('storage_management.html',
                         storage_areas=storage_areas,
                         products=products,
                         recent_transfers=recent_transfers)

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

# Production Machine Management - Master Data
@app.route('/production_machines', methods=['GET', 'POST'])
def production_machines():
    if request.method == 'POST':
        try:
            from models import ProductionMachine
            
            action = request.form.get('action')
            
            if action == 'add_machine':
                machine = ProductionMachine(
                    name=request.form['name'],
                    machine_type=request.form['machine_type'],
                    process_step=request.form['process_step'],
                    location=request.form.get('location', ''),
                    cleaning_frequency_hours=int(request.form.get('cleaning_frequency_hours', 3))
                )
                db.session.add(machine)
                db.session.commit()
                flash('Production machine added successfully!', 'success')
                
            elif action == 'toggle_machine':
                machine_id = int(request.form['machine_id'])
                machine = ProductionMachine.query.get(machine_id)
                if machine:
                    machine.is_active = not machine.is_active
                    machine.status = 'active' if machine.is_active else 'operational'
                    db.session.commit()
                    status_text = 'activated' if machine.is_active else 'deactivated'
                    flash(f'Machine {machine.name} {status_text}!', 'success')
                    
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    from models import ProductionMachine
    machines = ProductionMachine.query.all()
    
    # Group machines by process step
    machines_by_process = {}
    for machine in machines:
        if machine.process_step not in machines_by_process:
            machines_by_process[machine.process_step] = []
        machines_by_process[machine.process_step].append(machine)
    
    return render_template('production_machines.html', 
                         machines=machines,
                         machines_by_process=machines_by_process)

# Start Process with Machine Activation
@app.route('/start_process/<int:job_id>', methods=['POST'])
def start_process(job_id):
    try:
        from models import ProductionMachine, CleaningSchedule, ProductionOrderTracking
        
        job = ProductionJobNew.query.get_or_404(job_id)
        
        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.utcnow()
        job.process_start_time = datetime.utcnow()
        job.started_by = request.form.get('operator_name', 'Unknown')
        job.machines_active = True
        
        # Find machines for this process step
        machines = ProductionMachine.query.filter_by(process_step=job.stage).all()
        print(f"DEBUG: Looking for machines with process_step='{job.stage}', found {len(machines)} machines")
        
        # Activate machines and create cleaning schedules
        for machine in machines:
            machine.is_active = True
            machine.status = 'active'
            
            # Create cleaning schedules every 3 hours (or machine frequency)
            current_time = datetime.utcnow()
            frequency_hours = machine.cleaning_frequency_hours
            
            # Create initial cleaning schedule with adjusted frequency for testing
            if job.stage == 'cleaning_24h':
                # 5 minutes for 24h cleaning (testing)
                scheduled_time = current_time + timedelta(minutes=5)
            elif job.stage == 'cleaning_12h':
                # 2 minutes for 12h cleaning (testing)
                scheduled_time = current_time + timedelta(minutes=2)
            else:
                # Default to machine frequency for other processes
                scheduled_time = current_time + timedelta(hours=frequency_hours)
                
            first_cleaning = CleaningSchedule(
                machine_id=machine.id,
                job_id=job_id,
                production_order_id=job.order_id,
                process_step=job.stage,
                scheduled_time=scheduled_time
            )
            db.session.add(first_cleaning)
        
        # Create or update production order tracking
        tracking = ProductionOrderTracking.query.filter_by(production_order_id=job.order_id).first()
        if not tracking:
            tracking = ProductionOrderTracking(
                production_order_id=job.order_id,
                current_stage=job.stage,
                overall_status='in_progress',
                start_time=datetime.utcnow()
            )
            db.session.add(tracking)
        else:
            tracking.current_stage = job.stage
            tracking.overall_status = 'in_progress'
        
        db.session.commit()
        
        flash(f'Process {job.stage} started successfully! Machine cleaning schedules activated.', 'success')
        return redirect(url_for('production_execution'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error starting process: {str(e)}', 'error')
        return redirect(url_for('production_execution'))

# Stop Process with Machine Deactivation
@app.route('/stop_process/<int:job_id>', methods=['POST'])
def stop_process(job_id):
    try:
        from models import ProductionMachine, CleaningSchedule, ProductionOrderTracking
        
        job = ProductionJobNew.query.get_or_404(job_id)
        
        # Update job status
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        job.process_end_time = datetime.utcnow()
        job.completed_by = request.form.get('operator_name', 'Unknown')
        job.machines_active = False
        
        # Calculate process duration
        if job.process_start_time:
            duration = job.process_end_time - job.process_start_time
            hours = duration.total_seconds() / 3600
        
        # Deactivate machines for this process step
        machines = ProductionMachine.query.filter_by(process_step=job.stage).all()
        for machine in machines:
            machine.is_active = False
            machine.status = 'operational'
        
        # Cancel pending cleaning schedules for this job
        pending_schedules = CleaningSchedule.query.filter_by(
            job_id=job_id, 
            status='scheduled'
        ).all()
        for schedule in pending_schedules:
            schedule.status = 'cancelled'
        
        # Update production order tracking
        tracking = ProductionOrderTracking.query.filter_by(production_order_id=job.order_id).first()
        if tracking:
            # Check if this is the final stage
            if job.stage == 'packing':
                tracking.overall_status = 'completed'
                tracking.end_time = datetime.utcnow()
                if tracking.start_time:
                    total_duration = tracking.end_time - tracking.start_time
                    tracking.total_duration_hours = total_duration.total_seconds() / 3600
        
        db.session.commit()
        
        flash(f'Process {job.stage} stopped successfully! Machine cleaning schedules deactivated.', 'success')
        return redirect(url_for('production_execution'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error stopping process: {str(e)}', 'error')
        return redirect(url_for('production_execution'))

# Machine Cleaning for Active Processes
@app.route('/process_machine_cleaning/<int:job_id>', methods=['GET', 'POST'])
def process_machine_cleaning(job_id):
    from models import ProductionMachine, MachineCleaningLog, CleaningSchedule
    
    job = ProductionJobNew.query.get_or_404(job_id)
    
    # Get machines for this process step
    machines = ProductionMachine.query.filter_by(process_step=job.stage, is_active=True).all()
    
    # Get pending cleaning schedules
    pending_cleanings = CleaningSchedule.query.filter_by(
        job_id=job_id,
        status='scheduled'
    ).filter(CleaningSchedule.scheduled_time <= datetime.utcnow()).all()
    
    # Get recent cleaning logs for this job
    recent_logs = MachineCleaningLog.query.filter_by(job_id=job_id).order_by(
        MachineCleaningLog.cleaning_start_time.desc()
    ).limit(10).all()
    
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'start_cleaning':
                machine_id = int(request.form['machine_id'])
                machine = ProductionMachine.query.get(machine_id)
                
                # Handle photo upload
                before_photo = None
                if 'before_photo' in request.files:
                    file = request.files['before_photo']
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = f"machine_before_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
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
    
    return render_template('process_machine_cleaning.html',
                         job=job,
                         machines=machines,
                         pending_cleanings=pending_cleanings,
                         recent_logs=recent_logs)

@app.route('/complete_process_machine_cleaning/<int:log_id>', methods=['GET', 'POST'])
def complete_process_machine_cleaning(log_id):
    from models import MachineCleaningLog, CleaningSchedule, ProductionOrderTracking
    
    log = MachineCleaningLog.query.get_or_404(log_id)
    
    if request.method == 'POST':
        try:
            # Handle after photo upload
            after_photo = None
            if 'after_photo' in request.files:
                file = request.files['after_photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"machine_after_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    after_photo = filename
            
            # Complete the cleaning log
            log.cleaning_end_time = datetime.utcnow()
            log.photo_after = after_photo
            log.waste_collected_kg = float(request.form.get('waste_collected', 0))
            log.notes = request.form.get('notes', '')
            log.status = 'completed'
            
            # Calculate cleaning duration
            if log.cleaning_start_time:
                duration = log.cleaning_end_time - log.cleaning_start_time
                log.cleaning_duration_minutes = int(duration.total_seconds() / 60)
            
            # Update machine last cleaned time
            log.machine.last_cleaned = log.cleaning_end_time
            
            # Mark related cleaning schedule as completed
            schedule = CleaningSchedule.query.filter_by(
                machine_id=log.machine_id,
                job_id=log.job_id,
                status='scheduled'
            ).first()
            if schedule:
                schedule.status = 'completed'
            
            # Create next cleaning schedule with adjusted frequency for testing
            if log.process_step == 'cleaning_24h':
                # 5 minutes for 24h cleaning (testing)
                next_cleaning_time = log.cleaning_end_time + timedelta(minutes=5)
            elif log.process_step == 'cleaning_12h':
                # 2 minutes for 12h cleaning (testing)
                next_cleaning_time = log.cleaning_end_time + timedelta(minutes=2)
            else:
                # Default to machine frequency for other processes
                next_cleaning_time = log.cleaning_end_time + timedelta(hours=log.machine.cleaning_frequency_hours)
                
            next_schedule = CleaningSchedule(
                machine_id=log.machine_id,
                job_id=log.job_id,
                production_order_id=log.production_order_id,
                process_step=log.process_step,
                scheduled_time=next_cleaning_time
            )
            db.session.add(next_schedule)
            
            # Update production order tracking
            tracking = ProductionOrderTracking.query.filter_by(production_order_id=log.production_order_id).first()
            if tracking:
                tracking.total_cleanings_performed += 1
            
            db.session.commit()
            
            flash('Machine cleaning completed successfully!', 'success')
            return redirect(url_for('process_machine_cleaning', job_id=log.job_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing machine cleaning: {str(e)}', 'error')
    
    return render_template('complete_process_machine_cleaning.html', log=log)

# Production Order Comprehensive Tracking
@app.route('/production_order_tracking/<production_order_id>')
def production_order_tracking(production_order_id):
    from models import ProductionOrderTracking, MachineCleaningLog
    
    # Get all jobs for this production order
    jobs = ProductionJobNew.query.filter_by(order_id=production_order_id).order_by(ProductionJobNew.created_at).all()
    
    # Get tracking information
    tracking = ProductionOrderTracking.query.filter_by(production_order_id=production_order_id).first()
    
    # Get all cleaning logs for this production order
    cleaning_logs = MachineCleaningLog.query.filter_by(
        production_order_id=production_order_id
    ).order_by(MachineCleaningLog.cleaning_start_time).all()
    
    # Get process parameters from various stages
    process_data = {}
    for job in jobs:
        if job.stage == 'transfer':
            transfers = ProductionTransfer.query.filter_by(job_id=job.id).all()
            process_data['transfers'] = transfers
        elif job.stage == 'cleaning_24h':
            cleaning_24h = CleaningProcess.query.filter_by(job_id=job.id).all()
            process_data['cleaning_24h'] = cleaning_24h
        elif job.stage == 'cleaning_12h':
            cleaning_12h = CleaningProcess.query.filter_by(job_id=job.id).all()
            process_data['cleaning_12h'] = cleaning_12h
        elif job.stage == 'grinding':
            grinding = GrindingProcess.query.filter_by(job_id=job.id).all()
            process_data['grinding'] = grinding
        elif job.stage == 'packing':
            packing = PackingProcess.query.filter_by(job_id=job.id).all()
            process_data['packing'] = packing
    
    return render_template('production_order_tracking.html',
                         production_order_id=production_order_id,
                         jobs=jobs,
                         tracking=tracking,
                         cleaning_logs=cleaning_logs,
                         process_data=process_data)

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

@app.route('/api/production_jobs_by_stage')
def api_production_jobs_by_stage():
    """API endpoint to get production jobs organized by stage with workflow logic"""
    try:
        # Get all active jobs
        jobs = ProductionJobNew.query.filter(
            ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
        ).order_by(ProductionJobNew.created_at.desc()).all()
        
        # Organize jobs by stage
        jobs_by_stage = {
            'cleaning_24h': [],
            'cleaning_12h': [],
            'grinding': [],
            'packing': []
        }
        
        # Get running processes for status
        running_processes = []
        try:
            running_processes = CleaningProcess.query.filter_by(status='running').all()
        except:
            pass
        
        running_job_ids = [p.job_id for p in running_processes]
        
        for job in jobs:
            # Determine if this job can proceed based on workflow logic
            can_proceed = False
            is_previous_step = False
            is_running = job.id in running_job_ids
            
            # Get order to check overall workflow state
            order = ProductionOrder.query.get(job.order_id) if job.order_id else None
            
            if job.stage == 'cleaning_24h':
                # 24h cleaning can always start if pending, or restart if there's capacity
                can_proceed = job.status == 'pending' or (job.status == 'completed' and has_available_24h_capacity())
                is_previous_step = False  # This is the first step
                
            elif job.stage == 'cleaning_12h':
                # 12h cleaning can start if 24h is completed for this job
                previous_24h_job = ProductionJobNew.query.filter_by(
                    order_id=job.order_id, stage='cleaning_24h', status='completed'
                ).first()
                can_proceed = job.status == 'pending' and previous_24h_job is not None
                
                # Can restart 24h if 12h bin is available
                is_previous_step = job.status == 'completed' and has_available_24h_capacity()
                
            elif job.stage == 'grinding':
                # Grinding can start if 12h cleaning is completed
                previous_12h_job = ProductionJobNew.query.filter_by(
                    order_id=job.order_id, stage='cleaning_12h', status='completed'
                ).first()
                can_proceed = job.status == 'pending' and previous_12h_job is not None
                
                # Can restart 12h if grinding is not yet started
                is_previous_step = job.status in ['pending', 'completed'] and has_available_12h_capacity()
                
            elif job.stage == 'packing':
                # Packing can start if grinding is completed
                previous_grinding_job = ProductionJobNew.query.filter_by(
                    order_id=job.order_id, stage='grinding', status='completed'
                ).first()
                can_proceed = job.status == 'pending' and previous_grinding_job is not None
                
                # Can restart grinding if packing is not yet started
                is_previous_step = job.status in ['pending', 'completed']
            
            # Calculate progress
            progress = 0
            if job.status == 'completed':
                progress = 100
            elif job.status == 'in_progress' or is_running:
                progress = 50
            elif job.status == 'pending' and can_proceed:
                progress = 10
            
            job_data = {
                'id': job.id,
                'job_number': job.job_number,
                'order_number': order.order_number if order else 'N/A',
                'status': job.status,
                'stage': job.stage,
                'can_proceed': can_proceed,
                'is_previous_step': is_previous_step,
                'is_running': is_running,
                'progress': progress,
                'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else None,
                'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else None,
                'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else None
            }
            
            # Add to appropriate stage
            if job.stage in ['cleaning_24h', 'cleaning']:
                jobs_by_stage['cleaning_24h'].append(job_data)
            elif job.stage == 'cleaning_12h':
                jobs_by_stage['cleaning_12h'].append(job_data)
            elif job.stage == 'grinding':
                jobs_by_stage['grinding'].append(job_data)
            elif job.stage == 'packing':
                jobs_by_stage['packing'].append(job_data)
        
        return jsonify(jobs_by_stage)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def has_available_24h_capacity():
    """Check if there's available capacity for 24h cleaning"""
    try:
        # Check if there are available 24h cleaning bins
        available_bins = CleaningBin.query.filter_by(
            status='empty', 
            cleaning_type='24_hour'
        ).count()
        return available_bins > 0
    except:
        return True  # Default to true if can't check

def has_available_12h_capacity():
    """Check if there's available capacity for 12h cleaning"""
    try:
        # Check if there are available 12h cleaning bins
        available_bins = CleaningBin.query.filter_by(
            status='empty', 
            cleaning_type='12_hour'
        ).count()
        return available_bins > 0
    except:
        return True  # Default to true if can't check

# Removed duplicate route - using the comprehensive one above

@app.route('/mark_dispatch_delivered/<int:dispatch_id>')
def mark_dispatch_delivered(dispatch_id):
    """Mark dispatch as delivered and make vehicle available again"""
    try:
        from models import Dispatch, DispatchVehicle

        dispatch = Dispatch.query.get_or_404(dispatch_id)
        dispatch.status = 'delivered'
        dispatch.delivery_date = datetime.utcnow()

        # Make vehicle available again
        vehicle = DispatchVehicle.query.get(dispatch.vehicle_id)
        if vehicle:
            vehicle.status = 'available'

        db.session.commit()
        flash('Dispatch marked as delivered and vehicle is now available!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating dispatch: {str(e)}', 'error')

    return redirect(url_for('sales_dispatch'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        flash(f'File not found: {str(e)}', 'error')
        return redirect(url_for('sales_dispatch'))

@app.route('/api/storage_details/<int:storage_area_id>')
def api_storage_details(storage_area_id):
    """API endpoint to get detailed storage area information including products and bag details"""
    try:
        storage_area = StorageArea.query.get_or_404(storage_area_id)
        
        # Get all packing processes for this storage area
        packing_processes = PackingProcess.query.filter_by(storage_area_id=storage_area_id).all()
        
        # Get storage transfers to this area
        storage_transfers = StorageTransfer.query.filter_by(to_storage_id=storage_area_id).all()
        
        # Aggregate product data
        products_data = {}
        total_quantity = 0
        total_bags = 0
        
        # Process packing data
        for packing in packing_processes:
            product_name = packing.product.name
            product_category = packing.product.category
            
            if product_name not in products_data:
                products_data[product_name] = {
                    'name': product_name,
                    'category': product_category,
                    'total_quantity': 0,
                    'bag_details': [],
                    'shallow_storage': 0,
                    'last_updated': None,
                    'operators': set()
                }
            
            products_data[product_name]['total_quantity'] += packing.total_packed_kg
            products_data[product_name]['shallow_storage'] += packing.stored_in_shallow_kg
            products_data[product_name]['bag_details'].append({
                'bag_weight_kg': packing.bag_weight_kg,
                'number_of_bags': packing.number_of_bags,
                'total_packed_kg': packing.total_packed_kg,
                'packed_date': packing.packed_time.strftime('%d/%m/%Y %H:%M')
            })
            products_data[product_name]['operators'].add(packing.operator_name)
            
            # Update last updated time
            if not products_data[product_name]['last_updated'] or packing.packed_time > datetime.strptime(products_data[product_name]['last_updated'], '%d/%m/%Y %H:%M'):
                products_data[product_name]['last_updated'] = packing.packed_time.strftime('%d/%m/%Y %H:%M')
            
            total_quantity += packing.total_packed_kg + packing.stored_in_shallow_kg
            total_bags += packing.number_of_bags
        
        # Process storage transfer data
        for transfer in storage_transfers:
            product_name = transfer.product.name
            product_category = transfer.product.category
            
            if product_name not in products_data:
                products_data[product_name] = {
                    'name': product_name,
                    'category': product_category,
                    'total_quantity': 0,
                    'bag_details': [],
                    'shallow_storage': 0,
                    'last_updated': None,
                    'operators': set()
                }
            
            products_data[product_name]['total_quantity'] += transfer.quantity_kg
            products_data[product_name]['operators'].add(transfer.operator_name)
            
            # Update last updated time
            if not products_data[product_name]['last_updated'] or transfer.transfer_time > datetime.strptime(products_data[product_name]['last_updated'], '%d/%m/%Y %H:%M'):
                products_data[product_name]['last_updated'] = transfer.transfer_time.strftime('%d/%m/%Y %H:%M')
            
            total_quantity += transfer.quantity_kg
        
        # Convert sets to lists for JSON serialization
        for product in products_data.values():
            product['operators'] = list(product['operators'])
            if not product['last_updated']:
                product['last_updated'] = 'N/A'
        
        # Get recent activities
        recent_activities = []
        
        # Add recent packing activities
        recent_packing = PackingProcess.query.filter_by(storage_area_id=storage_area_id)\
                                           .order_by(PackingProcess.packed_time.desc())\
                                           .limit(5).all()
        for packing in recent_packing:
            recent_activities.append({
                'date_time': packing.packed_time.strftime('%d/%m/%Y %H:%M'),
                'activity_type': f'Packed {packing.product.name}',
                'quantity': f'{packing.total_packed_kg:.2f}',
                'operator': packing.operator_name
            })
        
        # Add recent transfer activities
        recent_transfers_in = StorageTransfer.query.filter_by(to_storage_id=storage_area_id)\
                                                 .order_by(StorageTransfer.transfer_time.desc())\
                                                 .limit(3).all()
        for transfer in recent_transfers_in:
            recent_activities.append({
                'date_time': transfer.transfer_time.strftime('%d/%m/%Y %H:%M'),
                'activity_type': f'Transfer In - {transfer.product.name}',
                'quantity': f'{transfer.quantity_kg:.2f}',
                'operator': transfer.operator_name
            })
        
        # Sort activities by date
        recent_activities.sort(key=lambda x: datetime.strptime(x['date_time'], '%d/%m/%Y %H:%M'), reverse=True)
        recent_activities = recent_activities[:10]  # Limit to 10 most recent
        
        utilization = (storage_area.current_stock_kg / storage_area.capacity_kg * 100) if storage_area.capacity_kg > 0 else 0
        
        response_data = {
            'storage_area': {
                'id': storage_area.id,
                'name': storage_area.name,
                'capacity_kg': storage_area.capacity_kg,
                'current_stock_kg': storage_area.current_stock_kg,
                'location': storage_area.location
            },
            'products': list(products_data.values()),
            'total_quantity': total_quantity,
            'total_bags': total_bags,
            'utilization': utilization,
            'recent_activities': recent_activities
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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