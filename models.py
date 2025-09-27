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
    from_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    to_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'))
    to_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'))
    quantity = db.Column(db.Float, nullable=False)
    transfer_time = db.Column(db.DateTime, default=datetime.utcnow)
    transfer_type = db.Column(db.String(30))  # godown_to_godown, godown_to_precleaning
    operator = db.Column(db.String(100))
    notes = db.Column(db.Text)
    evidence_photo = db.Column(db.String(255))

    # Relationships
    from_godown = db.relationship('Godown', foreign_keys=[from_godown_id])
    to_godown = db.relationship('Godown', foreign_keys=[to_godown_id])
    to_precleaning_bin = db.relationship('PrecleaningBin', foreign_keys=[to_precleaning_bin_id])

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    role = db.Column(db.String(50), nullable=False)  # admin, operator, lab_instructor
    phone = db.Column(db.String(20))
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PrecleaningProcess(db.Model):
    """Timer-based precleaning process"""
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfer.id'), nullable=False)
    from_godown_id = db.Column(db.Integer, db.ForeignKey('godown.id'), nullable=False)
    to_precleaning_bin_id = db.Column(db.Integer, db.ForeignKey('precleaning_bin.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    operator = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    timer_active = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='preparing')  # preparing, running, completed
    notes = db.Column(db.Text)
    evidence_photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transfer = db.relationship('Transfer', backref='precleaning_process')
    from_godown = db.relationship('Godown', foreign_keys=[from_godown_id])
    to_precleaning_bin = db.relationship('PrecleaningBin', foreign_keys=[to_precleaning_bin_id])

class PrecleaningReminder(db.Model):
    """Reminders for manual cleaning during precleaning process"""
    id = db.Column(db.Integer, primary_key=True)
    precleaning_process_id = db.Column(db.Integer, db.ForeignKey('precleaning_process.id'), nullable=False)
    due_time = db.Column(db.DateTime, nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    user_notified = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    reminder_sequence = db.Column(db.Integer, default=1)  # 1, 2, 3... for multiple reminders
    photo_uploaded = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    precleaning_process = db.relationship('PrecleaningProcess', backref='precleaning_reminders')