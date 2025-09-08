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

@app.route('/raw_wheat_quality_report', methods=['GET', 'POST'])
def raw_wheat_quality_report():
    if request.method == 'POST':
        try:
            vehicle_id = request.form['vehicle_id']
            vehicle = Vehicle.query.get_or_404(vehicle_id)

            # Parse test date
            test_date = datetime.strptime(request.form['test_date'], '%Y-%m-%d').date()

            report = RawWheatQualityReport()
            report.vehicle_id = int(vehicle_id)
            report.wheat_variety = request.form['wheat_variety']
            report.test_date = test_date
            report.bill_number = request.form.get('bill_number')

            # Parse arrival datetime if provided
            if request.form.get('arrival_datetime'):
                report.arrival_datetime = datetime.strptime(request.form['arrival_datetime'], '%Y-%m-%dT%H:%M')

            report.lab_chemist = request.form['lab_chemist']

            # Test parameters
            report.moisture = float(request.form.get('moisture', 0)) if request.form.get('moisture') else None
            report.hectoliter_weight = float(request.form.get('hectoliter_weight', 0)) if request.form.get('hectoliter_weight') else None
            report.wet_gluten = float(request.form.get('wet_gluten', 0)) if request.form.get('wet_gluten') else None
            report.dry_gluten = float(request.form.get('dry_gluten', 0)) if request.form.get('dry_gluten') else None
            report.sedimentation_value = float(request.form.get('sedimentation_value', 0)) if request.form.get('sedimentation_value') else None

            # Refractions/Impurities
            report.chaff_husk = float(request.form.get('chaff_husk', 0)) if request.form.get('chaff_husk') else None
            report.straws_sticks = float(request.form.get('straws_sticks', 0)) if request.form.get('straws_sticks') else None
            report.other_foreign_matter = float(request.form.get('other_foreign_matter', 0)) if request.form.get('other_foreign_matter') else None
            report.mudballs = float(request.form.get('mudballs', 0)) if request.form.get('mudballs') else None
            report.stones = float(request.form.get('stones', 0)) if request.form.get('stones') else None
            report.dust_sand = float(request.form.get('dust_sand', 0)) if request.form.get('dust_sand') else None
            report.total_impurities = float(request.form.get('total_impurities', 0)) if request.form.get('total_impurities') else None

            # Grain dockage
            report.shriveled_wheat = float(request.form.get('shriveled_wheat', 0)) if request.form.get('shriveled_wheat') else None
            report.insect_damage = float(request.form.get('insect_damage', 0)) if request.form.get('insect_damage') else None
            report.blackened_wheat = float(request.form.get('blackened_wheat', 0)) if request.form.get('blackened_wheat') else None
            report.other_grains = float(request.form.get('other_grains', 0)) if request.form.get('other_grains') else None
            report.soft_wheat = float(request.form.get('soft_wheat', 0)) if request.form.get('soft_wheat') else None
            report.heat_damaged = float(request.form.get('heat_damaged', 0)) if request.form.get('heat_damaged') else None
            report.immature_wheat = float(request.form.get('immature_wheat', 0)) if request.form.get('immature_wheat') else None
            report.broken_wheat = float(request.form.get('broken_wheat', 0)) if request.form.get('broken_wheat') else None
            report.total_dockage = float(request.form.get('total_dockage', 0)) if request.form.get('total_dockage') else None

            # Final assessment
            report.comments_action = request.form.get('comments_action')
            report.category_assigned = request.form['category_assigned']
            report.approved = request.form.get('approved') == 'on'

            # Update vehicle status if approved
            if report.approved:
                vehicle.status = 'approved'
                vehicle.quality_category = request.form['category_assigned']
                vehicle.owner_approved = True
            else:
                vehicle.status = 'quality_check'
                vehicle.quality_category = request.form['category_assigned']

            db.session.add(report)
            db.session.commit()
            flash('Raw wheat quality report saved successfully!', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error saving quality report: {str(e)}', 'error')

    pending_vehicles = Vehicle.query.filter_by(status='pending').all()
    raw_wheat_reports = RawWheatQualityReport.query.join(Vehicle).order_by(RawWheatQualityReport.created_at.desc()).all()

    return render_template('raw_wheat_quality_report.html', vehicles=pending_vehicles, raw_wheat_reports=raw_wheat_reports)

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
            # Handle file uploads
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

                # Check if all jobs for this order are completed
                check_and_update_order_completion(job.order_id)

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
        active_jobs = ProductionJobNew.query.filter(
            ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
        ).order_by(ProductionJobNew.created_at.desc()).all()

        jobs_by_stage = {
            'transfer': [],
            'cleaning_24h': [],
            'cleaning_12h': [],
            'grinding': [],
            'packing': []
        }

        for job in active_jobs:
            try:
                # Safe attribute access with fallbacks
                order_number = 'N/A'
                order = None
                try:
                    order = job.order
                    if order:
                        order_number = order.order_number
                except Exception:
                    pass

                job_data = {
                    'id': job.id,
                    'job_number': job.job_number or 'Unknown',
                    'order_number': order_number,
                    'status': job.status or 'unknown',
                    'stage': job.stage or 'unknown',
                    'progress': 100 if job.status == 'completed' else 50 if job.status == 'in_progress' else 0,
                    'can_proceed': job.status == 'pending',
                    'is_previous_step': False,
                    'is_running': job.status == 'in_progress',
                    'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
                    'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else '',
                    'started_by': job.started_by or '',
                    'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else '',
                    'completed_by': job.completed_by or ''
                }

                stage = job.stage or 'unknown'
                if stage in jobs_by_stage:
                    jobs_by_stage[stage].append(job_data)
                else:
                    app.logger.warning(f"Unknown job stage: {stage}")

            except Exception as job_error:
                app.logger.error(f"Error processing job {job.id}: {str(job_error)}")
                continue

        return jsonify({
            'success': True,
            'jobs': jobs_by_stage,
            'total_jobs': len(active_jobs)
        })

    except Exception as e:
        app.logger.error(f"Critical error in production_jobs_by_stage: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'jobs': {
                'transfer': [],
                'cleaning_24h': [],
                'cleaning_12h': [],
                'grinding': [],
                'packing': []
            }
        }), 500

@app.route('/api/job_details/<int:job_id>')
def api_job_details(job_id):
    """API endpoint to get detailed job information"""
    try:
        job = ProductionJobNew.query.get(job_id)

        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        # Safe attribute access
        order_number = 'N/A'
        if hasattr(job, 'order') and job.order:
            order_number = getattr(job.order, 'order_number', 'N/A')

        job_data = {
            'id': getattr(job, 'id', 0),
            'job_number': getattr(job, 'job_number', 'Unknown'),
            'order_number': order_number,
            'status': getattr(job, 'status', 'unknown'),
            'stage': getattr(job, 'stage', 'unknown'),
            'created_at': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
            'started_at': job.started_at.strftime('%Y-%m-%d %H:%M') if job.started_at else '',
            'started_by': getattr(job, 'started_by', '') or '',
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M') if job.completed_at else '',
            'completed_by': getattr(job, 'completed_by', '') or '',
            'notes': getattr(job, 'notes', '') or ''
        }

        return jsonify({'success': True, 'job': job_data})

    except Exception as e:
        app.logger.error(f"Error in job_details API for job {job_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/available_production_orders')
def api_available_production_orders():
    """API endpoint to get orders ready for production execution"""
    try:
        # Get orders that have approved plans but no jobs created yet
        orders_with_plans = db.session.query(ProductionOrder).join(ProductionPlan).filter(
            ProductionPlan.status == 'approved',
            ProductionOrder.status == 'planned'
        ).all()

        orders_data = []
        for order in orders_with_plans:
            # Check if jobs already exist for this order
            existing_jobs = ProductionJobNew.query.filter_by(order_id=order.id).count()
            if existing_jobs == 0:  # Only include orders without existing jobs
                order_data = {
                    'id': order.id,
                    'order_number': order.order_number,
                    'product': order.product,
                    'quantity': order.quantity,
                    'priority': order.priority,
                    'created_at': order.created_at.strftime('%Y-%m-%d') if order.created_at else ''
                }
                orders_data.append(order_data)

        return jsonify({'success': True, 'orders': orders_data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'orders': []}), 200

@app.route('/api/process_control/<int:job_id>/<stage>')
def api_process_control(job_id, stage):
    """API endpoint to get process control information"""
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
            'started_by': job.started_by
        }

        return jsonify({'success': True, 'job': job_data, 'stage': stage})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/start_production_execution/<int:order_id>', methods=['GET', 'POST'])
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
            job.started_by = request.form.get('operator_name', 'System')
            job.notes = f'Auto-created job for {stage} stage'
            job.created_at = datetime.now()

            db.session.add(job)

        # Update order status
        order.status = 'in_progress'

        # Update plan status to executed
        plan.status = 'executed'

        db.session.commit()
        flash('Production execution started! All jobs have been created.', 'success')
        return redirect(url_for('production_execution'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error starting production execution: {str(e)}')
        flash(f'Error starting production execution: {str(e)}', 'error')
        return redirect(url_for('production_planning', order_id=order_id))

@app.route('/production_execution/transfer_setup/<int:job_id>', methods=['GET', 'POST'])
def transfer_setup(job_id):
    """Set up transfer process"""
    job = ProductionJobNew.query.get_or_404(job_id)
    plan = ProductionPlan.query.get_or_404(job.plan_id)
    plan_items = ProductionPlanItem.query.filter_by(plan_id=plan.id).all()

    if request.method == 'POST':
        try:
            # Process the transfer setup
            operator_name = request.form['operator_name']
            from_bin_ids = request.form.getlist('from_bin_id')
            quantities = request.form.getlist('quantity')

            total_transferred = 0

            for i, from_bin_id in enumerate(from_bin_ids):
                if from_bin_id and quantities[i]:
                    quantity = float(quantities[i])

                    # Create transfer record
                    transfer = ProductionTransfer()
                    transfer.job_id = job_id
                    transfer.from_precleaning_bin_id = int(from_bin_id)
                    transfer.quantity = quantity
                    transfer.transfer_type = 'precleaning_to_cleaning'
                    transfer.operator_name = operator_name
                    transfer.transfer_time = datetime.now()

                    # Update bin stocks
                    from_bin = PrecleaningBin.query.get(int(from_bin_id))
                    if from_bin:
                        from_bin.current_stock -= quantity

                    db.session.add(transfer)
                    total_transferred += quantity

            # Update job status
            job.status = 'in_progress'
            job.started_at = datetime.now()
            job.started_by = operator_name

            db.session.commit()

            flash(f'Transfer process started! Transferred {total_transferred} kg total.', 'success')
            return redirect(url_for('production_execution'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error in transfer process: {str(e)}', 'error')

    return render_template('transfer_execution_setup.html', job=job, plan_items=plan_items)

@app.route('/production_execution/cleaning_setup/<int:job_id>', methods=['GET', 'POST'])
def cleaning_setup(job_id):
    """Set up 24-hour cleaning process"""
    job = ProductionJobNew.query.get_or_404(job_id)
    # Get available cleaning bins
    cleaning_bins = CleaningBin.query.filter_by(status='available').all()

    if request.method == 'POST':
        return redirect(url_for('process_cleaning_24h', job_id=job_id))

    return render_template('cleaning_setup.html', job=job, cleaning_bins=cleaning_bins)

@app.route('/production_execution/cleaning_12h_setup/<int:job_id>', methods=['GET', 'POST'])
def cleaning_12h_setup(job_id):
    """Set up 12-hour cleaning process"""
    job = ProductionJobNew.query.get_or_404(job_id)

    if request.method == 'POST':
        return redirect(url_for('production_execution'))

    return render_template('cleaning_12h_setup.html', job=job)

@app.route('/production_execution/b1_scale/<int:job_id>', methods=['GET', 'POST'])
def b1_scale_process(job_id):
    """B1 scale and grinding process"""
    job = ProductionJobNew.query.get_or_404(job_id)

    if request.method == 'POST':
        return redirect(url_for('production_execution'))

    return render_template('b1_scale_process.html', job=job)

@app.route('/production_execution/packing/<int:job_id>')
def packing_execution_route(job_id):
    """Redirect to existing packing execution"""
    return redirect(url_for('packing_execution', job_id=job_id))

def check_and_update_order_completion(order_id):
    """Check if all jobs for an order are completed and update order status"""
    try:
        order = ProductionOrder.query.get(order_id)
        if not order:
            return

        # Get all jobs for this order
        all_jobs = ProductionJobNew.query.filter_by(order_id=order_id).all()

        if not all_jobs:
            return

        # Check if all jobs are completed
        completed_jobs = [job for job in all_jobs if job.status == 'completed']

        if len(completed_jobs) == len(all_jobs):
            # All jobs completed - mark order as completed
            order.status = 'completed'
            db.session.commit()
            print(f"Order {order.order_number} marked as completed - all {len(all_jobs)} jobs finished")
    except Exception as e:
        print(f"Error checking order completion: {str(e)}")

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

@app.route('/api/start_job/<int:job_id>/<stage>', methods=['POST'])
def api_start_job(job_id, stage):
    """API endpoint to start a specific job stage"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)

        # Check if job can be started (previous stage completed)
        if not can_start_job(job, stage):
            return jsonify({
                'success': False,
                'error': 'Previous stage must be completed before starting this job'
            })

        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.now()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Job {job.job_number} started for {stage}',
            'redirect_url': f'/production_execution/{stage}_setup/{job_id}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/complete_job/<int:job_id>', methods=['POST'])
def api_complete_job(job_id):
    """API endpoint to complete a job"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)

        job.status = 'completed'
        job.completed_at = datetime.now()
        job.completed_by = request.json.get('completed_by', 'System')

        db.session.commit()

        # Check if this completes the entire order
        check_and_update_order_completion(job.order_id)

        return jsonify({
            'success': True,
            'message': f'Job {job.job_number} completed successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/job_timer/<int:job_id>')
def api_job_timer(job_id):
    """API endpoint to get job timer information"""
    try:
        job = ProductionJobNew.query.get_or_404(job_id)

        # Get associated cleaning process if exists
        cleaning_process = CleaningProcess.query.filter_by(job_id=job_id).first()

        timer_info = {
            'job_id': job_id,
            'status': job.status,
            'has_timer': False,
            'time_remaining': None,
            'end_time': None
        }

        if cleaning_process and cleaning_process.status == 'running':
            timer_info['has_timer'] = True
            timer_info['end_time'] = cleaning_process.end_time.isoformat()

            if cleaning_process.end_time > datetime.now():
                time_remaining = cleaning_process.end_time - datetime.now()
                timer_info['time_remaining'] = {
                    'hours': int(time_remaining.total_seconds() // 3600),
                    'minutes': int((time_remaining.total_seconds() % 3600) // 60),
                    'seconds': int(time_remaining.total_seconds() % 60)
                }
            else:
                timer_info['time_remaining'] = {'hours': 0, 'minutes': 0, 'seconds': 0}

        return jsonify({
            'success': True,
            'timer': timer_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def can_start_job(job, stage):
    """Check if a job can be started based on dependencies"""
    stage_order = ['transfer', 'cleaning_24h', 'cleaning_12h', 'grinding', 'packing']

    try:
        current_index = stage_order.index(stage)
    except ValueError:
        return False

    if current_index == 0:  # Transfer can always start
        return True

    # Check if previous stage is completed
    previous_stage = stage_order[current_index - 1]
    previous_job = ProductionJobNew.query.filter_by(
        order_id=job.order_id,
        stage=previous_stage
    ).first()

    return previous_job and previous_job.status == 'completed'

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

# Comprehensive Production View Routes
@app.route('/enhanced_production_workflow')
def enhanced_production_workflow():
    """Enhanced Production Workflow View - 4-Step Process Implementation"""
    try:
        # Get active production orders that are ready for the enhanced workflow
        active_orders = ProductionOrder.query.filter(
            ProductionOrder.status.in_(['planned', 'in_progress'])
        ).order_by(ProductionOrder.created_at.desc()).all()

        # Get all production jobs grouped by stage for the enhanced workflow
        jobs_by_stage = {
            'transfer': ProductionJobNew.query.filter_by(stage='transfer').filter(
                ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
            ).order_by(ProductionJobNew.created_at.desc()).all(),

            'cleaning_24h': ProductionJobNew.query.filter_by(stage='cleaning_24h').filter(
                ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
            ).order_by(ProductionJobNew.created_at.desc()).all(),

            'cleaning_12h': ProductionJobNew.query.filter_by(stage='cleaning_12h').filter(
                ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
            ).order_by(ProductionJobNew.created_at.desc()).all(),

            'grinding': ProductionJobNew.query.filter_by(stage='grinding').filter(
                ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
            ).order_by(ProductionJobNew.created_at.desc()).all(),

            'packing': ProductionJobNew.query.filter_by(stage='packing').filter(
                ProductionJobNew.status.in_(['pending', 'in_progress', 'completed'])
            ).order_by(ProductionJobNew.created_at.desc()).all()
        }

        # Get active cleaning processes with countdown timers
        active_24h_processes = CleaningProcess.query.filter_by(
            process_type='24_hour', status='running'
        ).all()

        active_12h_processes = CleaningProcess.query.filter_by(
            process_type='12_hour', status='running'
        ).all()

        # Get active grinding processes with timer display
        active_grinding_processes = GrindingProcess.query.filter_by(status='in_progress').all()

        # Get recent cleaning reminders and logs
        recent_cleaning_logs = CleaningLog.query.order_by(
            CleaningLog.cleaning_time.desc()
        ).limit(10).all()

        return render_template('enhanced_production_workflow.html',
                             active_orders=active_orders,
                             jobs_by_stage=jobs_by_stage,
                             active_24h_processes=active_24h_processes,
                             active_12h_processes=active_12h_processes,
                             active_grinding_processes=active_grinding_processes,
                             recent_cleaning_logs=recent_cleaning_logs)

    except Exception as e:
        flash(f'Error loading enhanced production workflow: {str(e)}', 'error')
        return redirect(url_for('index'))

# Enhanced Production Workflow API Endpoints
@app.route('/api/start_24h_cleaning_process', methods=['POST'])
def api_start_24h_cleaning_process():
    """API endpoint to start 24-hour cleaning process with countdown timer"""
    try:
        order_id = request.json.get('order_id')
        duration_hours = float(request.json.get('duration_hours', 24))
        start_moisture = float(request.json.get('start_moisture'))
        operator_name = request.json.get('operator_name')
        water_added = float(request.json.get('water_added', 0))

        order = ProductionOrder.query.get_or_404(order_id)

        # Find or create a production plan for this order
        plan = ProductionPlan.query.filter_by(order_id=order_id).first()
        if not plan:
            plan = ProductionPlan()
            plan.order_id = order_id
            plan.planned_by = operator_name
            plan.status = 'approved'
            db.session.add(plan)
            db.session.flush()

        # Create a new job for this order if it doesn't exist
        job = ProductionJobNew.query.filter_by(order_id=order_id, stage='cleaning_24h').first()
        if not job:
            job = ProductionJobNew()
            job.order_id = order_id
            job.plan_id = plan.id
            job.stage = 'cleaning_24h'
            job.job_number = f"J24H-{order.order_number}"
            job.status = 'pending'
            db.session.add(job)
            db.session.flush()

        # Create new cleaning process
        cleaning_process = CleaningProcess()
        cleaning_process.job_id = job.id
        cleaning_process.process_type = '24_hour'
        cleaning_process.duration_hours = duration_hours
        cleaning_process.start_time = datetime.now()
        cleaning_process.end_time = datetime.now() + timedelta(hours=duration_hours)
        cleaning_process.start_moisture = start_moisture
        cleaning_process.water_added_liters = water_added
        cleaning_process.operator_name = operator_name
        cleaning_process.status = 'running'
        cleaning_process.is_locked = True

        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.now()
        job.started_by = operator_name

        db.session.add(cleaning_process)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '24-hour cleaning process started successfully',
            'process_id': cleaning_process.id,
            'end_time': cleaning_process.end_time.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start_12h_cleaning_process', methods=['POST'])
def api_start_12h_cleaning_process():
    """API endpoint to start 12-hour cleaning process with countdown timer"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['order_id', 'duration_hours', 'start_moisture', 'target_moisture', 'operator_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        # Convert and validate numeric values
        try:
            order_id = int(data.get('order_id'))
            duration_hours = float(data.get('duration_hours'))
            start_moisture = float(data.get('start_moisture'))
            target_moisture = float(data.get('target_moisture'))
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': 'Invalid numeric values provided'}), 400
        
        # Validate ranges
        if duration_hours <= 0:
            return jsonify({'success': False, 'error': 'Duration must be greater than 0'}), 400
        if not (0 <= start_moisture <= 100):
            return jsonify({'success': False, 'error': 'Start moisture must be between 0-100%'}), 400
        if not (0 <= target_moisture <= 100):
            return jsonify({'success': False, 'error': 'Target moisture must be between 0-100%'}), 400

        operator_name = data.get('operator_name').strip()
        if not operator_name:
            return jsonify({'success': False, 'error': 'Operator name is required'}), 400

        order = ProductionOrder.query.get_or_404(order_id)

        # Find or create a production plan for this order
        plan = ProductionPlan.query.filter_by(order_id=order_id).first()
        if not plan:
            plan = ProductionPlan()
            plan.order_id = order_id
            plan.planned_by = operator_name
            plan.status = 'approved'
            db.session.add(plan)
            db.session.flush()

        # Create a new job for this order if it doesn't exist
        job = ProductionJobNew.query.filter_by(order_id=order_id, stage='cleaning_12h').first()
        if not job:
            job = ProductionJobNew()
            job.order_id = order_id
            job.plan_id = plan.id
            job.stage = 'cleaning_12h'
            job.job_number = f"J12H-{order.order_number}"
            job.status = 'pending'
            db.session.add(job)
            db.session.flush()

        # Create new cleaning process
        cleaning_process = CleaningProcess()
        cleaning_process.job_id = job.id
        cleaning_process.process_type = '12_hour'
        cleaning_process.duration_hours = duration_hours
        cleaning_process.start_time = datetime.now()
        cleaning_process.end_time = datetime.now() + timedelta(hours=duration_hours)
        cleaning_process.start_moisture = start_moisture
        cleaning_process.target_moisture = target_moisture
        cleaning_process.operator_name = operator_name
        cleaning_process.status = 'running'
        cleaning_process.is_locked = True

        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.now()
        job.started_by = operator_name

        db.session.add(cleaning_process)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '12-hour cleaning process started successfully',
            'process_id': cleaning_process.id,
            'end_time': cleaning_process.end_time.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/start_grinding_process', methods=['POST'])
def api_start_grinding_process():
    """API endpoint to start grinding process with start/stop timer"""
    try:
        order_id = request.json.get('order_id')
        machine_name = request.json.get('machine_name')
        input_quantity = float(request.json.get('input_quantity'))
        operator_name = request.json.get('operator_name')
        b1_scale_operator = request.json.get('b1_scale_operator')
        b1_scale_weight = float(request.json.get('b1_scale_weight'))

        order = ProductionOrder.query.get_or_404(order_id)

        # Find or create a production plan for this order
        plan = ProductionPlan.query.filter_by(order_id=order_id).first()
        if not plan:
            plan = ProductionPlan()
            plan.order_id = order_id
            plan.planned_by = operator_name
            plan.status = 'approved'
            db.session.add(plan)
            db.session.flush()

        # Create a new job for this order if it doesn't exist
        job = ProductionJobNew.query.filter_by(order_id=order_id, stage='grinding').first()
        if not job:
            job = ProductionJobNew()
            job.order_id = order_id
            job.plan_id = plan.id
            job.stage = 'grinding'
            job.job_number = f"JGR-{order.order_number}"
            job.status = 'pending'
            db.session.add(job)
            db.session.flush()

        # Create new grinding process
        grinding_process = GrindingProcess()
        grinding_process.job_id = job.id
        grinding_process.machine_name = machine_name
        grinding_process.start_time = datetime.now()
        grinding_process.input_quantity_kg = input_quantity
        grinding_process.operator_name = operator_name
        grinding_process.b1_scale_operator = b1_scale_operator
        grinding_process.b1_scale_start_time = datetime.now()
        grinding_process.b1_scale_weight_kg = b1_scale_weight
        grinding_process.status = 'in_progress'

        # Update job status
        job.status = 'in_progress'
        job.started_at = datetime.now()
        job.started_by = operator_name

        db.session.add(grinding_process)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Grinding process started successfully',
            'process_id': grinding_process.id,
            'start_time': grinding_process.start_time.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop_grinding_process', methods=['POST'])
def api_stop_grinding_process():
    """API endpoint to stop grinding process and capture output"""
    try:
        process_id = request.json.get('process_id')
        total_output_kg = float(request.json.get('total_output_kg'))
        main_products_kg = float(request.json.get('main_products_kg'))
        bran_kg = float(request.json.get('bran_kg'))

        grinding_process = GrindingProcess.query.get_or_404(process_id)

        # Update process with completion data
        grinding_process.end_time = datetime.now()
        grinding_process.total_output_kg = total_output_kg
        grinding_process.main_products_kg = main_products_kg
        grinding_process.bran_kg = bran_kg
        grinding_process.status = 'completed'

        # Calculate percentages
        if total_output_kg > 0:
            grinding_process.bran_percentage = (bran_kg / total_output_kg) * 100
            grinding_process.main_products_percentage = (main_products_kg / total_output_kg) * 100

            # Flag if bran percentage > 25%
            if grinding_process.bran_percentage > 25:
                grinding_process.bran_percentage_alert = True

        # Update job status
        job = grinding_process.job
        job.status = 'completed'
        job.completed_at = datetime.now()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Grinding process completed successfully',
            'bran_percentage': grinding_process.bran_percentage,
            'main_products_percentage': grinding_process.main_products_percentage,
            'bran_alert': grinding_process.bran_percentage_alert
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/record_cleaning', methods=['POST'])
def api_record_cleaning():
    try:
        process_id = request.form.get('process_id')
        process_type = request.form.get('process_type')
        cleaned_by = request.form.get('cleaned_by')
        notes = request.form.get('notes')
        cleaning_duration = request.form.get('cleaning_duration', 5)

        # Handle file uploads
        before_photo = request.files.get('before_photo')
        after_photo = request.files.get('after_photo')

        before_filename = None
        after_filename = None

        if before_photo and before_photo.filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            before_filename = f"cleaning_before_{timestamp}_{secure_filename(before_photo.filename)}"
            before_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], before_filename))

        if after_photo and after_photo.filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            after_filename = f"cleaning_after_{timestamp}_{secure_filename(after_photo.filename)}"
            after_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], after_filename))

        # Create cleaning log entry
        cleaning_log = CleaningLog(
            process_id=process_id,
            cleaned_by=cleaned_by,
            cleaning_time=datetime.now(),
            photo_before=before_filename,
            photo_after=after_filename,
            notes=notes,
            cleaning_duration_minutes=int(cleaning_duration)
        )

        db.session.add(cleaning_log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Cleaning recorded successfully!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/complete_cleaning_process', methods=['POST'])
def api_complete_cleaning_process():
    try:
        data = request.get_json()
        process_id = data.get('process_id')

        if not process_id:
            return jsonify({
                'success': False,
                'error': 'Process ID is required'
            }), 400

        # Try to find the process in CleaningProcess table
        cleaning_process = CleaningProcess.query.get(process_id)

        if cleaning_process:
            cleaning_process.status = 'completed'
            cleaning_process.end_time = datetime.now()
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Cleaning process completed successfully!'
            })

        # If not found in CleaningProcess, try GrindingProcess
        grinding_process = GrindingProcess.query.get(process_id)

        if grinding_process:
            grinding_process.status = 'completed'
            grinding_process.end_time = datetime.now()
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Grinding process completed successfully!'
            })

        return jsonify({
            'success': False,
            'error': 'Process not found'
        }), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get_active_timers')
def api_get_active_timers():
    """API endpoint to get all active timers and countdowns"""
    try:
        # Get active cleaning processes
        active_24h = CleaningProcess.query.filter_by(
            process_type='24_hour', status='running'
        ).all()

        active_12h = CleaningProcess.query.filter_by(
            process_type='12_hour', status='running'
        ).all()

        # Get active grinding processes
        active_grinding = GrindingProcess.query.filter_by(status='in_progress').all()

        timers = {
            'cleaning_24h': [
                {
                    'id': process.id,
                    'job_id': process.job_id,
                    'start_time': process.start_time.isoformat(),
                    'end_time': process.end_time.isoformat(),
                    'operator': process.operator_name
                } for process in active_24h
            ],
            'cleaning_12h': [
                {
                    'id': process.id,
                    'job_id': process.job_id,
                    'start_time': process.start_time.isoformat(),
                    'end_time': process.end_time.isoformat(),
                    'operator': process.operator_name
                } for process in active_12h
            ],
            'grinding': [
                {
                    'id': process.id,
                    'job_id': process.job_id,
                    'start_time': process.start_time.isoformat(),
                    'machine_name': process.machine_name,
                    'operator': process.operator_name
                } for process in active_grinding
            ]
        }

        return jsonify({
            'success': True,
            'timers': timers
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/api/cleaning_reminders')
def get_cleaning_reminders():
    """API endpoint to get active cleaning reminders"""
    try:
        # Get machines that need cleaning
        reminders = []
        machines = ProductionMachine.query.all()

        for machine in machines:
            # Check if machine has cleaning reminders
            reminder = MachineCleaningReminder.query.filter_by(
                machine_id=machine.id, 
                is_active=True
            ).first()

            if reminder:
                # Calculate if cleaning is due
                now = datetime.utcnow()
                if reminder.next_cleaning_due and now >= reminder.next_cleaning_due:
                    reminders.append({
                        'id': reminder.id,
                        'machine_name': machine.name,
                        'machine_type': machine.machine_type,
                        'frequency_hours': reminder.frequency_hours,
                        'last_cleaned': reminder.last_cleaned_at.isoformat() if reminder.last_cleaned_at else None,
                        'next_due': reminder.next_cleaning_due.isoformat() if reminder.next_cleaning_due else None,
                        'status': 'overdue' if now > reminder.next_cleaning_due else 'due'
                    })

        return jsonify(reminders)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/confirm_cleaning', methods=['POST'])
def confirm_cleaning():
    """API endpoint to confirm machine cleaning"""
    try:
        data = request.get_json()
        reminder_id = data.get('reminder_id')
        confirmed_by = data.get('confirmed_by')

        reminder = MachineCleaningReminder.query.get_or_404(reminder_id)

        # Create cleaning confirmation
        confirmation = CleaningConfirmation(
            reminder_id=reminder_id,
            confirmed_by=confirmed_by,
            confirmed_at=datetime.utcnow()
        )

        # Update reminder
        reminder.last_cleaned_at = datetime.utcnow()
        reminder.next_cleaning_due = datetime.utcnow() + timedelta(hours=reminder.frequency_hours)
        reminder.reminder_sent = False

        db.session.add(confirmation)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Cleaning confirmed successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/production_order_details/<int:order_id>')
def production_order_details(order_id):
    """Detailed view of production order with all captured data and durations"""
    try:
        order = ProductionOrder.query.get_or_404(order_id)
        jobs = ProductionJobNew.query.filter_by(order_id=order_id).order_by(ProductionJobNew.created_at).all()

        # Get all stage parameters for this order
        stage_data = {}
        total_duration = 0
        total_buffer_time = 0

        for job in jobs:
            parameters = StageParameters.query.filter_by(job_id=job.id).all()

            # Calculate job duration
            job_duration = 0
            if job.started_at and job.completed_at:
                job_duration = (job.completed_at - job.started_at).total_seconds() / 3600
                total_duration += job_duration

            stage_data[job.stage] = {
                'job': job,
                'parameters': parameters,
                'duration_hours': job_duration
            }

            # Add buffer times
            for param in parameters:
                if param.buffer_duration_minutes:
                    total_buffer_time += param.buffer_duration_minutes

        # Convert buffer time to hours
        total_buffer_hours = total_buffer_time / 60

        # Get cleaning compliance
        cleaning_logs = []
        for job in jobs:
            machine_cleanings = CleaningConfirmation.query.join(MachineCleaningReminder).join(ProductionMachine).filter(
                ProductionMachine.process_step == job.stage
            ).all()
            cleaning_logs.extend(machine_cleanings)

        return render_template('production_order_details.html',
                             order=order,
                             stage_data=stage_data,
                             total_duration=total_duration,
                             total_buffer_hours=total_buffer_hours,
                             cleaning_logs=cleaning_logs)

    except Exception as e:
        flash(f'Error loading order details: {str(e)}', 'error')
        return redirect(url_for('index'))

# Cleaning Reminder System with Configurable Frequencies
@app.route('/configure_cleaning_frequencies', methods=['GET', 'POST'])
def configure_cleaning_frequencies():
    """Configure cleaning frequencies for production machines"""
    if request.method == 'POST':
        try:
            machine_id = request.form.get('machine_id')
            frequency_hours = float(request.form.get('frequency_hours'))

            machine = ProductionMachine.query.get_or_404(machine_id)

            # Check if reminder already exists
            existing_reminder = MachineCleaningReminder.query.filter_by(
                machine_id=machine_id, 
                is_active=True
            ).first()

            if existing_reminder:
                # Update existing reminder
                existing_reminder.frequency_hours = frequency_hours
                existing_reminder.next_cleaning_due = datetime.utcnow() + timedelta(hours=frequency_hours)
            else:
                # Create new reminder
                reminder = MachineCleaningReminder(
                    machine_id=machine_id,
                    frequency_hours=frequency_hours,
                    next_cleaning_due=datetime.utcnow() + timedelta(hours=frequency_hours),
                    is_active=True
                )
                db.session.add(reminder)

            db.session.commit()
            flash(f'Cleaning frequency updated for {machine.name}', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating cleaning frequency: {str(e)}', 'error')

        return redirect(url_for('configure_cleaning_frequencies'))

    # Get all machines and their current reminders
    machines = ProductionMachine.query.all()
    machine_reminders = {}

    for machine in machines:
        reminder = MachineCleaningReminder.query.filter_by(
            machine_id=machine.id, 
            is_active=True
        ).first()
        machine_reminders[machine.id] = reminder

    return render_template('configure_cleaning_frequencies.html', 
                         machines=machines, 
                         machine_reminders=machine_reminders)

def check_cleaning_reminders():
    """Background function to check and send cleaning reminders"""
    try:
        now = datetime.utcnow()
        overdue_reminders = MachineCleaningReminder.query.filter(
            MachineCleaningReminder.is_active == True,
            MachineCleaningReminder.next_cleaning_due <= now,
            MachineCleaningReminder.reminder_sent == False
        ).all()

        for reminder in overdue_reminders:
            # Mark as reminder sent to avoid duplicate alerts
            reminder.reminder_sent = True

            # In a real system, you would send email/SMS notifications here
            # For now, we'll just log the reminder
            print(f"CLEANING REMINDER: {reminder.machine.name} is due for cleaning!")

        if overdue_reminders:
            db.session.commit()

    except Exception as e:
        print(f"Error checking cleaning reminders: {str(e)}")

# Initialize sample cleaning reminders for existing machines
@app.route('/production_orders', methods=['GET', 'POST'])
def production_orders():
    if request.method == 'POST':
        try:
            production_order = ProductionOrder()
            production_order.order_number = generate_order_number('PO')
            production_order.quantity = float(request.form['quantity'])
            production_order.product_id = int(request.form['product_id']) if request.form.get('product_id') else None

            production_order.deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d')
            production_order.priority = request.form.get('priority', 'normal')
            production_order.notes = request.form.get('notes')
            production_order.created_by = request.form['created_by']

            db.session.add(production_order)
            db.session.commit()
            flash('Production order created successfully!', 'success')
            return redirect(url_for('production_orders'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production order: {str(e)}', 'error')

    orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    products = Product.query.filter_by(category='Main Product').all()

    return render_template('production_orders.html', orders=orders, products=products)

@app.route('/production_planning/<int:order_id>', methods=['GET', 'POST'])
def production_planning(order_id):
    order = ProductionOrder.query.get_or_404(order_id)

    if request.method == 'POST':
        try:
            # Create production plan
            plan = ProductionPlan()
            plan.order_id = order_id
            plan.planned_by = request.form['planned_by']
            plan.status = 'approved'

            db.session.add(plan)
            db.session.flush()  # Get plan ID

            # Create plan items
            bin_ids = request.form.getlist('bin_id')
            percentages = request.form.getlist('percentage')

            total_percentage = 0
            for i, bin_id in enumerate(bin_ids):
                if bin_id and percentages[i]:
                    percentage = float(percentages[i])
                    quantity = (order.quantity * percentage) / 100

                    plan_item = ProductionPlanItem()
                    plan_item.plan_id = plan.id
                    plan_item.precleaning_bin_id = int(bin_id)
                    plan_item.percentage = percentage
                    plan_item.quantity = quantity

                    db.session.add(plan_item)
                    total_percentage += percentage

            plan.total_percentage = total_percentage
            order.status = 'planned'

            db.session.commit()
            flash('Production plan created successfully!', 'success')
            return redirect(url_for('production_orders'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating production plan: {str(e)}', 'error')

    precleaning_bins = PrecleaningBin.query.filter(PrecleaningBin.current_stock > 0).all()
    existing_plan = ProductionPlan.query.filter_by(order_id=order_id).first()

    return render_template('production_planning.html', order=order, bins=precleaning_bins, plan=existing_plan)

@app.route('/production_execution')
def production_execution():
    # Get all active production jobs
    active_jobs = ProductionJobNew.query.filter(
        ProductionJobNew.status.in_(['pending', 'in_progress'])
    ).order_by(ProductionJobNew.created_at.desc()).all()

    # Get orders ready for execution (planned but no jobs created yet)
    ready_orders = db.session.query(ProductionOrder).join(ProductionPlan).filter(
        ProductionPlan.status == 'approved',
        ProductionOrder.status == 'planned',
        ~ProductionOrder.id.in_(
            db.session.query(ProductionJobNew.order_id).distinct()
        )
    ).all()

    return render_template('production_execution.html', jobs=active_jobs, ready_orders=ready_orders)

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