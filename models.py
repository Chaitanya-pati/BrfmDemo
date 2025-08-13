from datetime import datetime, timedelta
from app import db
from sqlalchemy import func

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
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
    name = db.Column(db.String(100), nullable=False)
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
    vehicle_photo_before = db.Column(db.String(200))
    vehicle_photo_after = db.Column(db.String(200))
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
    quality_notes = db.Column(db.Text)
    lab_instructor = db.Column(db.String(100))
    test_time = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    to_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
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
    production_jobs = db.relationship('ProductionJob', backref='order', lazy=True)

class ProductionPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    planned_by = db.Column(db.String(100), nullable=False)
    planning_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_percentage = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='draft')  # draft, approved, executed
    
    # Relationship
    plan_items = db.relationship('ProductionPlanItem', backref='plan', lazy=True)

class ProductionPlanItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('production_plan.id'), nullable=False)
    precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # calculated from percentage
    
    # Relationship
    precleaning_bin = db.relationship('PrecleaningBin', backref='plan_items')

class ProductionJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('production_order.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)  # transfer, cleaning_24h, cleaning_12h, grinding
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    assigned_to = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    quantity = db.Column(db.Float)
    moisture_in = db.Column(db.Float)
    moisture_out = db.Column(db.Float)
    target_moisture = db.Column(db.Float)
    evidence_photo_start = db.Column(db.String(200))
    evidence_photo_end = db.Column(db.String(200))
    notes = db.Column(db.Text)

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
    
    # Relationship
    dispatch_items = db.relationship('DispatchItem', backref='dispatch', lazy=True)

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
