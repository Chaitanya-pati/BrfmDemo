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
    transfers_from = db.relationship('Transfer', foreign_keys='Transfer.from_godown_id', lazy=True)
    transfers_to = db.relationship('Transfer', foreign_keys='Transfer.to_godown_id', lazy=True)

class PrecleaningBin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Float, nullable=False)  # in tons
    current_stock = db.Column(db.Float, default=0)

    # Relationship
    transfers_to = db.relationship('Transfer', foreign_keys='Transfer.to_precleaning_bin_id', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Main Product or Bran
    description = db.Column(db.Text)
    # unit and standard_price columns don't exist in database, removing to match schema

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
    __tablename__ = 'transfer'

    id = db.Column(db.Integer, primary_key=True)
    from_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'), nullable=True)
    to_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'), nullable=True)
    from_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=True)
    to_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    transfer_type = db.Column(db.String(50), nullable=False)  # 'godown_to_precleaning', 'precleaning_to_cleaning', etc.
    operator = db.Column(db.String(100), nullable=False)
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    evidence_photo = db.Column(db.String(255))

    # Relationships
    from_godown = db.relationship('Godown', foreign_keys=[from_godown_id], overlaps="transfers_from")
    to_godown = db.relationship('Godown', foreign_keys=[to_godown_id], overlaps="transfers_to")
    from_precleaning_bin = db.relationship('PrecleaningBin', foreign_keys=[from_precleaning_bin_id])
    to_precleaning_bin = db.relationship('PrecleaningBin', foreign_keys=[to_precleaning_bin_id], overlaps="transfers_to")

# Enhanced Models for Production Stage Tracking
class StageParameters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_name = db.Column(db.String(50), nullable=False)
    parameter_name = db.Column(db.String(100), nullable=False)
    parameter_value = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MachineCleaningReminder(db.Model):
    """Configurable cleaning reminders for production machines"""
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('production_machine.id'), nullable=False)
    frequency_hours = db.Column(db.Float, nullable=False)  # Configurable frequency
    last_cleaned_at = db.Column(db.DateTime)
    next_cleaning_due = db.Column(db.DateTime)
    reminder_sent = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # machine relationship removed - ProductionMachine model deleted

class CleaningConfirmation(db.Model):
    """Tracks user confirmations of machine cleaning"""
    id = db.Column(db.Integer, primary_key=True)
    reminder_id = db.Column(db.Integer, db.ForeignKey('machine_cleaning_reminder.id'), nullable=False)
    confirmed_by = db.Column(db.String(100), nullable=False)
    confirmed_at = db.Column(db.DateTime, default=datetime.utcnow)
    cleaning_duration_minutes = db.Column(db.Float)
    before_photo = db.Column(db.String(255))
    after_photo = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    reminder = db.relationship('MachineCleaningReminder', backref=db.backref('confirmations', lazy=True))

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    # job_id removed - production functionality deleted
    cleaning_bin_id = db.Column(db.Integer, db.ForeignKey('cleaning_bin.id'))
    process_type = db.Column(db.String(20), nullable=False)  # '24_hour', '12_hour', 'custom'
    duration_hours = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    actual_end_time = db.Column(db.DateTime)
    start_moisture = db.Column(db.Float)
    end_moisture = db.Column(db.Float)
    target_moisture = db.Column(db.Float)  # For 12-hour cleaning
    water_added_liters = db.Column(db.Float, default=0.0)
    waste_collected_kg = db.Column(db.Float, default=0.0)
    machine_name = db.Column(db.String(100))
    operator_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, paused
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Enhanced tracking fields for step requirements
    buffer_time_minutes = db.Column(db.Float, default=0.0)  # Buffer timing for total duration
    buffer_start_time = db.Column(db.DateTime)  # When buffer time started
    buffer_end_time = db.Column(db.DateTime)    # When buffer time ended
    is_locked = db.Column(db.Boolean, default=True, nullable=True)  # Locks access during cleaning
    reminder_sent_5min = db.Column(db.Boolean, default=False, nullable=True)
    reminder_sent_10min = db.Column(db.Boolean, default=False, nullable=True)
    reminder_sent_30min = db.Column(db.Boolean, default=False, nullable=True)
    # next_process_job_id removed - production functionality deleted
    
    # Additional tracking for 12-hour process start parameters
    start_parameters_captured = db.Column(db.Boolean, default=False)
    completion_parameters_captured = db.Column(db.Boolean, default=False)

    # job relationships removed - production functionality deleted

class GrindingProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # job_id removed - production functionality deleted
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

    # job relationship removed - production functionality deleted

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
    # job_id removed - production functionality deleted
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    bag_weight_kg = db.Column(db.Float, nullable=False)  # 30, 50, 25 kg bags
    number_of_bags = db.Column(db.Integer, nullable=False)
    total_packed_kg = db.Column(db.Float, nullable=False)
    packed_time = db.Column(db.DateTime, default=datetime.utcnow)
    operator_name = db.Column(db.String(100), nullable=False)
    storage_area_id = db.Column(db.Integer, db.ForeignKey('storage_area.id'))
    stored_in_shallow_kg = db.Column(db.Float, default=0)
    packing_photo = db.Column(db.String(255))

    # job relationship removed - production functionality deleted
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
    # job_id removed - production functionality deleted
    process_type = db.Column(db.String(50), nullable=False)  # cleaning_24h, cleaning_12h, machine_cleaning
    reminder_time = db.Column(db.DateTime, nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)  # 5min, 10min, 30min
    status = db.Column(db.String(20), default='pending')  # pending, sent, dismissed
    message = db.Column(db.Text)

    # job relationship removed - production functionality deleted

# Enhanced Machine Cleaning System - Process Linked
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

# Enhanced cleaning log linked to production processes

# Cleaning schedules and reminders for active processes

# Production Order comprehensive tracking

class RawWheatQualityReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    wheat_variety = db.Column(db.String(50), nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    bill_number = db.Column(db.String(50))
    arrival_datetime = db.Column(db.DateTime)
    lab_chemist = db.Column(db.String(100), nullable=False)

    # Test parameters
    moisture = db.Column(db.Float)
    hectoliter_weight = db.Column(db.Float)
    wet_gluten = db.Column(db.Float)
    dry_gluten = db.Column(db.Float)
    sedimentation_value = db.Column(db.Float)

    # Refractions/Impurities
    chaff_husk = db.Column(db.Float)
    straws_sticks = db.Column(db.Float)
    other_foreign_matter = db.Column(db.Float)
    mudballs = db.Column(db.Float)
    stones = db.Column(db.Float)
    dust_sand = db.Column(db.Float)
    total_impurities = db.Column(db.Float)

    # Grain dockage
    shriveled_wheat = db.Column(db.Float)
    insect_damage = db.Column(db.Float)
    blackened_wheat = db.Column(db.Float)
    other_grains = db.Column(db.Float)
    soft_wheat = db.Column(db.Float)
    heat_damaged = db.Column(db.Float)
    immature_wheat = db.Column(db.Float)
    broken_wheat = db.Column(db.Float)
    total_dockage = db.Column(db.Float)

    # Final assessment
    comments_action = db.Column(db.Text)
    category_assigned = db.Column(db.String(50), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vehicle = db.relationship('Vehicle', backref='raw_wheat_reports')