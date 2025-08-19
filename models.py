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
    test_result = db.Column(db.String(50))
    tested_by = db.Column(db.String(100))
    quality_notes = db.Column(db.Text)
    notes = db.Column(db.Text)
    lab_instructor = db.Column(db.String(100))
    test_time = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)

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
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
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

class CleaningProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('production_job_new.id'), nullable=False)
    process_type = db.Column(db.String(20), nullable=False)  # 24_hour, 12_hour
    cleaning_bin_id = db.Column(db.Integer, nullable=False)  # Which cleaning bin
    duration_hours = db.Column(db.Integer, nullable=False)
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
    notes = db.Column(db.Text)
    
    job = db.relationship('ProductionJobNew', backref=db.backref('cleaning_processes', lazy=True))

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

# Enhanced models already exist above - removing duplicates
