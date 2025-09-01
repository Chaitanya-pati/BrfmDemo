from datetime import datetime, timedelta
from app import db
from sqlalchemy import func

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    vehicles = db.relationship('Vehicle', backref='supplier', lazy=True)

class GodownType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # mill, low mill, hd
    description = db.Column(db.String(200))
    
    # Relationship
    godowns = db.relationship('Godown', backref='godown_type', lazy=True)

class Godown(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('godown_type.id'), nullable=False)
    capacity = db.Column(db.Float, default=0)  # in tons
    current_stock = db.Column(db.Float, default=0)  # in tons
    
    # Relationship
    transfers_from = db.relationship('Transfer', foreign_keys='Transfer.from_godown_id', backref='from_godown', lazy=True)
    transfers_to = db.relationship('Transfer', foreign_keys='Transfer.to_godown_id', backref='to_godown', lazy=True)

class PrecleaningBin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Float, nullable=False)  # in tons
    current_stock = db.Column(db.Float, default=0)
    
    # Relationship
    transfers_to = db.relationship('Transfer', foreign_keys='Transfer.to_precleaning_bin_id', backref='to_precleaning_bin', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Main Product or Bran
    description = db.Column(db.Text)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    arrival_time = db.Column(db.DateTime, default=datetime.utcnow)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    bill_photo = db.Column(db.String(200))  # file path
    vehicle_photo = db.Column(db.String(200))
    vehicle_photo_before = db.Column(db.String(200))
    vehicle_photo_after = db.Column(db.String(200))
    supplier_bill = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, quality_check, approved, rejected, unloaded
    quality_category = db.Column(db.String(50))  # low mill, mill, etc
    owner_approved = db.Column(db.Boolean, default=False)
    net_weight_before = db.Column(db.Float)
    net_weight_after = db.Column(db.Float)
    final_weight = db.Column(db.Float)
    godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    quality_tests = db.relationship('QualityTest', backref='vehicle', lazy=True)

class QualityTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    sample_bags_tested = db.Column(db.Integer, nullable=False)
    total_bags = db.Column(db.Integer, nullable=False)
    category_assigned = db.Column(db.String(50), nullable=False)
    moisture_content = db.Column(db.Float)
    foreign_matter = db.Column(db.Float)
    broken_grains = db.Column(db.Float)
    shrivelled_broken = db.Column(db.Float)  # Shrivelled & Broken
    damaged = db.Column(db.Float)  # Damaged
    weevilled = db.Column(db.Float)  # Weevilled
    other_food_grains = db.Column(db.Float)  # Other food grains
    sprouted = db.Column(db.Float)  # Sprouted
    immature = db.Column(db.Float)  # Immature
    test_weight = db.Column(db.Float)  # Test weight per hectolitre
    gluten = db.Column(db.Float)  # Gluten content
    protein = db.Column(db.Float)  # Protein content
    falling_number = db.Column(db.Float)  # Falling number
    ash_content = db.Column(db.Float)  # Ash content
    wet_gluten = db.Column(db.Float)  # Wet gluten
    dry_gluten = db.Column(db.Float)  # Dry gluten
    sedimentation_value = db.Column(db.Float)  # Sedimentation value
    test_result = db.Column(db.String(50))
    tested_by = db.Column(db.String(100))
    quality_notes = db.Column(db.Text)
    notes = db.Column(db.Text)
    lab_instructor = db.Column(db.String(100))
    test_time = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    sample_photos_before = db.Column(db.String(200))  # file path for before photos
    sample_photos_after = db.Column(db.String(200))   # file path for after photos

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    to_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    from_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'))
    to_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'))
    quantity = db.Column(db.Float, nullable=False)
    transfer_type = db.Column(db.String(50), nullable=False)  # godown_to_precleaning, precleaning_to_cleaning, etc
    operator = db.Column(db.String(100))
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    evidence_photo = db.Column(db.String(200))

class CleaningMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    machine_type = db.Column(db.String(50), nullable=False)  # drum_shield, magnet, separator
    cleaning_frequency_hours = db.Column(db.Integer, default=3)
    location = db.Column(db.String(100))
    last_cleaned = db.Column(db.DateTime)
    
    # Relationship
    cleaning_logs = db.relationship('CleaningLog', backref='machine', lazy=True)

class CleaningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('cleaning_machine.id'), nullable=False)
    cleaned_by = db.Column(db.String(100), nullable=False)
    cleaning_time = db.Column(db.DateTime, default=datetime.utcnow)
    photo_before = db.Column(db.String(200))
    photo_after = db.Column(db.String(200))
    waste_collected = db.Column(db.Float)  # in kg
    notes = db.Column(db.Text)

class ProductionOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    quantity = db.Column(db.Float, nullable=False)  # in tons
    product = db.Column(db.String(100))  # Change to string field instead of foreign key
    finished_good_type = db.Column(db.String(100))  # Type of finished good
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='normal')
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, planned, in_progress, completed
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    target_completion = db.Column(db.DateTime)
    
    # Relationships
    production_plan = db.relationship('ProductionPlan', backref='order', uselist=False)
    production_jobs = db.relationship('ProductionJobNew', back_populates='order', lazy=True)

class ProductionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    planned_by = db.Column(db.String(100), nullable=False)
    planning_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_percentage = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='draft')  # draft, approved, executed
    
    # Relationship
    plan_items = db.relationship('ProductionPlanItem', backref='plan', lazy=True)
    jobs = db.relationship('ProductionJobNew', back_populates='plan', lazy=True)

class ProductionPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('production_plan.id'), nullable=False)
    precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # calculated from percentage
    
    # Relationship
    precleaning_bin = db.relationship('PrecleaningBin', backref='plan_items')

# Removed duplicate ProductionJob - using the enhanced version below

class FinishedGoodsStorage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Float)
    current_stock = db.Column(db.Float, default=0)

class FinishedGoods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    storage_type = db.Column(db.String(20))  # bags, shallow
    bag_weight = db.Column(db.Float)  # 25kg, 30kg, 50kg
    bag_count = db.Column(db.Integer)
    storage_id = db.Column(db.Integer, db.ForeignKey('finished_goods_storage.id'))
    production_date = db.Column(db.DateTime, default=datetime.utcnow)
    batch_number = db.Column(db.String(50))
    
    # Relationships
    product = db.relationship('Product', backref='finished_goods')
    storage = db.relationship('FinishedGoodsStorage', backref='stored_goods')

class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    salesman = db.Column(db.String(100))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    total_quantity = db.Column(db.Float, nullable=False)
    delivered_quantity = db.Column(db.Float, default=0)
    pending_quantity = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, partial, completed
    
    # Relationships
    customer = db.relationship('Customer', backref='sales_orders')
    order_items = db.relationship('SalesOrderItem', backref='sales_order', lazy=True)
    dispatches = db.relationship('Dispatch', backref='sales_order', lazy=True)

class SalesOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    delivered_quantity = db.Column(db.Float, default=0)
    pending_quantity = db.Column(db.Float)
    
    # Relationship
    product = db.relationship('Product', backref='sales_order_items')

class DispatchVehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    capacity = db.Column(db.Float)
    status = db.Column(db.String(20), default='available')  # available, dispatched, blocked
    
    # Relationship
    dispatches = db.relationship('Dispatch', backref='vehicle', lazy=True)

class Dispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_number = db.Column(db.String(50), unique=True, nullable=False)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('dispatch_vehicle.id'), nullable=False)
    dispatch_date = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Float, nullable=False)
    loading_photo = db.Column(db.String(200))
    loaded_photo = db.Column(db.String(200))
    delivery_proof = db.Column(db.String(200))
    status = db.Column(db.String(20), default='loaded')  # loaded, in_transit, delivered
    delivered_by = db.Column(db.String(100))
    delivery_date = db.Column(db.DateTime)

class SalesDispatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    dispatch_date = db.Column(db.Date)
    vehicle_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))

class DispatchItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatch.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    bag_count = db.Column(db.Integer)
    
    # Relationship
    product = db.relationship('Product', backref='dispatch_items')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, operator, lab_instructor, production_manager
    phone = db.Column(db.String(20))
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CleaningReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('cleaning_machine.id'), nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    user_notified = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Enhanced Production Execution Models for Step-by-Step Production Tracking
class ProductionJobNew(db.Model):
    __tablename__ = 'production_job_new'
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('production_plan.id'), nullable=False)
    stage = db.Column(db.String(50), nullable=False)  # transfer, cleaning_24h, cleaning_12h, grinding, packing
    status = db.Column(db.String(50), default='pending')  # pending, in_progress, completed, paused
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    started_by = db.Column(db.String(100))
    completed_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('ProductionOrder', back_populates='production_jobs')
    plan = db.relationship('ProductionPlan', back_populates='jobs')

class ProductionTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    from_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=False)
    quantity_transferred = db.Column(db.Float, nullable=False)
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    start_photo = db.Column(db.String(255))
    end_photo = db.Column(db.String(255))
    
    job = db.relationship('ProductionJobNew', backref=db.backref('transfers', lazy=True))
    from_bin = db.relationship('PrecleaningBin', backref=db.backref('transfers', lazy=True))

class CleaningBin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Float, nullable=False)  # in tons
    current_stock = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='empty')  # empty, occupied, cleaning
    location = db.Column(db.String(100))
    cleaning_type = db.Column(db.String(20), default='24_hour')  # 24_hour, 12_hour
    
    # Relationship
    cleaning_processes = db.relationship('CleaningProcess', backref='cleaning_bin', lazy=True)

class CleaningProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    process_type = db.Column(db.String(50), nullable=False)  # 24_hour, 12_hour
    cleaning_bin_id = db.Column(db.Integer, db.ForeignKey('cleaning_bin.id'), nullable=False)
    duration_hours = db.Column(db.Float, nullable=False)
    target_moisture = db.Column(db.Float)  # For 12-hour process
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    actual_end_time = db.Column(db.DateTime)
    start_moisture = db.Column(db.Float)
    end_moisture = db.Column(db.Float)
    water_added_liters = db.Column(db.Float)
    waste_collected_kg = db.Column(db.Float)
    machine_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, running, completed
    start_photo = db.Column(db.String(255))
    end_photo = db.Column(db.String(255))
    operator_name = db.Column(db.String(100))
    completed_by = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced tracking fields for step requirements
    is_locked = db.Column(db.Boolean, default=True, nullable=True)  # Locks access during cleaning
    reminder_sent_5min = db.Column(db.Boolean, default=False, nullable=True)
    reminder_sent_10min = db.Column(db.Boolean, default=False, nullable=True)
    reminder_sent_30min = db.Column(db.Boolean, default=False, nullable=True)
    next_process_job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=True)  # For 12h process after 24h
    
    job = db.relationship('ProductionJobNew', foreign_keys=[job_id], backref=db.backref('cleaning_processes', lazy=True))
    next_process_job = db.relationship('ProductionJobNew', foreign_keys=[next_process_job_id], backref=db.backref('previous_cleaning_processes', lazy=True))

class GrindingProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    machine_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    input_quantity_kg = db.Column(db.Float, nullable=False)
    total_output_kg = db.Column(db.Float)
    main_products_kg = db.Column(db.Float)  # Should be 75-77%
    bran_kg = db.Column(db.Float)  # Should be 23-25%
    bran_percentage = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    operator_name = db.Column(db.String(100))
    start_photo = db.Column(db.String(255))
    end_photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    # Enhanced fields for B1 scale tracking
    b1_scale_operator = db.Column(db.String(100))  # B1 scale operator
    b1_scale_start_time = db.Column(db.DateTime)  # When wheat moved from B1 scale
    b1_scale_weight_kg = db.Column(db.Float)  # Weight from B1 scale
    
    # Bran percentage validation
    bran_percentage_alert = db.Column(db.Boolean, default=False)  # True if bran > 25%
    main_products_percentage = db.Column(db.Float)  # Calculated main products %
    
    job = db.relationship('ProductionJobNew', backref=db.backref('grinding_processes', lazy=True))

class ProductOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grinding_process_id = db.Column(db.Integer, db.ForeignKey('grinding_process.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_produced_kg = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    
    grinding_process = db.relationship('GrindingProcess', backref=db.backref('product_outputs', lazy=True))
    product = db.relationship('Product', backref=db.backref('production_outputs', lazy=True))

class PackingProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    bag_weight_kg = db.Column(db.Float, nullable=False)  # 30, 50, 25 kg bags
    number_of_bags = db.Column(db.Integer, nullable=False)
    total_packed_kg = db.Column(db.Float, nullable=False)
    packed_time = db.Column(db.DateTime, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    storage_area_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'))
    stored_in_shallow_kg = db.Column(db.Float, default=0)
    packing_photo = db.Column(db.String(255))
    
    job = db.relationship('ProductionJobNew', backref=db.backref('packing_processes', lazy=True))
    product = db.relationship('Product', backref=db.backref('packing_processes', lazy=True))
    storage_area = db.relationship('StorageArea', backref=db.backref('packed_goods', lazy=True))

class StorageArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity_kg = db.Column(db.Float, nullable=False)
    current_stock_kg = db.Column(db.Float, default=0)
    location = db.Column(db.String(200))
    
class StorageTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_storage_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'), nullable=False)
    to_storage_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(200))
    
    from_storage = db.relationship('StorageArea', foreign_keys=[from_storage_id], backref=db.backref('outgoing_transfers', lazy=True))
    to_storage = db.relationship('StorageArea', foreign_keys=[to_storage_id], backref=db.backref('incoming_transfers', lazy=True))
    product = db.relationship('Product', backref=db.backref('storage_transfers', lazy=True))

class ProcessReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    process_type = db.Column(db.String(50), nullable=False)  # cleaning_24h, cleaning_12h, machine_cleaning
    reminder_time = db.Column(db.DateTime, nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)  # 5min, 10min, 30min
    status = db.Column(db.String(20), default='pending')  # pending, sent, dismissed
    message = db.Column(db.Text)
    
    job = db.relationship('ProductionJobNew', backref=db.backref('reminders', lazy=True))

# Enhanced Machine Cleaning Model for Hourly Cleaning with B1 Scale
class B1ScaleCleaning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_name = db.Column(db.String(100), default='B1 Scale', nullable=False)
    cleaning_frequency_minutes = db.Column(db.Integer, default=60)  # Every hour
    last_cleaned = db.Column(db.DateTime)
    next_cleaning_due = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='due')  # due, cleaning, completed
    
    # Cleaning log relationship
    cleaning_logs = db.relationship('B1ScaleCleaningLog', backref='machine', lazy=True)
    
class B1ScaleCleaningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('b1_scale_cleaning.id'), nullable=False)
    grinding_process_id = db.Column(db.Integer, db.ForeignKey('grinding_process.id'))
    cleaned_by = db.Column(db.String(100), nullable=False)
    cleaning_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    cleaning_end_time = db.Column(db.DateTime)
    before_cleaning_photo = db.Column(db.String(255))
    after_cleaning_photo = db.Column(db.String(255))
    waste_collected_kg = db.Column(db.Float)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='completed')
    
    # Relationship with grinding process
    grinding_process = db.relationship('GrindingProcess', backref='b1_cleaning_logs')

# Enhanced Storage with 4 storage areas as requested
class ProductStorageTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_storage_area_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'), nullable=False)
    to_storage_area_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    bag_count = db.Column(db.Integer)
    bag_weight_kg = db.Column(db.Float)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Relationships
    from_storage = db.relationship('StorageArea', foreign_keys=[from_storage_area_id], backref='outbound_transfers')
    to_storage = db.relationship('StorageArea', foreign_keys=[to_storage_area_id], backref='inbound_transfers')
    product = db.relationship('Product', backref='storage_transfer_records')

# Enhanced Machine Cleaning System - Process Linked
class ProductionMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    machine_type = db.Column(db.String(50), nullable=False)
    process_step = db.Column(db.String(50), nullable=False)  # 'precleaning', 'cleaning_24h', 'cleaning_12h', 'grinding', 'packing'
    location = db.Column(db.String(100))
    cleaning_frequency_hours = db.Column(db.Integer, default=3)  # Default 3 hours
    last_cleaned = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='operational')
    is_active = db.Column(db.Boolean, default=False)  # Active during process
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cleaning_logs = db.relationship('MachineCleaningLog', backref='machine', lazy=True)
    cleaning_schedules = db.relationship('CleaningSchedule', backref='machine', lazy=True)

# Enhanced cleaning log linked to production processes
class MachineCleaningLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('production_machine.id'), nullable=False)
    production_order_id = db.Column(db.String(50))  # Link to production order
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'))  # Link to specific job
    process_step = db.Column(db.String(50), nullable=False)
    cleaned_by = db.Column(db.String(100), nullable=False)
    cleaning_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    cleaning_end_time = db.Column(db.DateTime)
    photo_before = db.Column(db.String(255))
    photo_after = db.Column(db.String(255))
    waste_collected_kg = db.Column(db.Float)
    cleaning_duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Cleaning schedules and reminders for active processes
class CleaningSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('production_machine.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    production_order_id = db.Column(db.String(50), nullable=False)
    process_step = db.Column(db.String(50), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, overdue, completed, cancelled
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Production Order comprehensive tracking
class ProductionOrderTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.String(50), unique=True, nullable=False)
    total_stages = db.Column(db.Integer, default=5)  # precleaning, 24h, 12h, grinding, packing
    current_stage = db.Column(db.String(50))
    overall_status = db.Column(db.String(20), default='pending')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    total_duration_hours = db.Column(db.Float)
    total_cleanings_performed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Process parameters tracking
    precleaning_moisture = db.Column(db.Float)
    cleaning_24h_start_moisture = db.Column(db.Float)
    cleaning_24h_end_moisture = db.Column(db.Float)
    cleaning_12h_start_moisture = db.Column(db.Float)
    cleaning_12h_end_moisture = db.Column(db.Float)
    grinding_input_kg = db.Column(db.Float)
    grinding_output_kg = db.Column(db.Float)
    grinding_bran_percentage = db.Column(db.Float)
    packing_total_bags = db.Column(db.Integer)
    packing_total_weight_kg = db.Column(db.Float)
