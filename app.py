
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_apscheduler import APScheduler

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-change-this-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///wheat_processing.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_sample_data():
    """Initialize sample data for testing"""
    try:
        # Import models here to avoid circular imports
        from models import GodownType, Godown, PrecleaningBin, Supplier, Product, Customer
        from datetime import timedelta, datetime
        
        # Create godown types
        if not db.session.query(GodownType).first():
            mill_type = GodownType(name='Mill', description='Regular mill quality wheat')
            low_mill_type = GodownType(name='Low Mill', description='Lower quality wheat')
            hd_type = GodownType(name='HD', description='High density wheat')
            
            db.session.add_all([mill_type, low_mill_type, hd_type])
            db.session.commit()
        
        # Create sample godowns
        if not db.session.query(Godown).first():
            godown1 = Godown(name='Godown A', type_id=1, capacity=100.0)
            godown2 = Godown(name='Godown B', type_id=2, capacity=150.0)
            godown3 = Godown(name='Godown C', type_id=3, capacity=200.0)
            
            db.session.add_all([godown1, godown2, godown3])
            db.session.commit()
        
        # Create sample precleaning bins
        if not db.session.query(PrecleaningBin).first():
            bin1 = PrecleaningBin(name='Pre-cleaning Bin 1', capacity=50.0)
            bin2 = PrecleaningBin(name='Pre-cleaning Bin 2', capacity=75.0)
            bin3 = PrecleaningBin(name='Pre-cleaning Bin 3', capacity=60.0)
            
            db.session.add_all([bin1, bin2, bin3])
            db.session.commit()
        
        # Create sample suppliers
        if not db.session.query(Supplier).first():
            supplier1 = Supplier(
                company_name='ABC Wheat Suppliers',
                contact_person='John Doe',
                phone='9876543210',
                city='Delhi'
            )
            supplier2 = Supplier(
                company_name='XYZ Grain Traders',
                contact_person='Jane Smith',
                phone='9876543211',
                city='Mumbai'
            )
            
            db.session.add_all([supplier1, supplier2])
            db.session.commit()
        
        # Create sample products
        if not db.session.query(Product).first():
            maida = Product(name='Maida', category='Main Product', description='Refined wheat flour')
            suji = Product(name='Suji', category='Main Product', description='Semolina')
            chakki_ata = Product(name='Chakki Ata', category='Main Product', description='Whole wheat flour')
            bran = Product(name='Bran', category='Bran', description='Wheat bran')
            
            db.session.add_all([maida, suji, chakki_ata, bran])
            db.session.commit()
        
        # Create sample customers
        if not db.session.query(Customer).first():
            customer1 = Customer(
                company_name='ABC Bakery',
                contact_person='Ram Kumar',
                phone='9876543220',
                city='Delhi'
            )
            customer2 = Customer(
                company_name='XYZ Food Products',
                contact_person='Shyam Gupta',
                phone='9876543221',
                city='Mumbai'
            )
            
            db.session.add_all([customer1, customer2])
            db.session.commit()
        
        # Create cleaning bins for 24h and 12h processes
        from models import CleaningBin
        if not db.session.query(CleaningBin).first():
            cleaning_bins = [
                CleaningBin(name='24-Hour Cleaning Bin #1', capacity=100.0, status='empty', cleaning_type='24_hour'),
                CleaningBin(name='24-Hour Cleaning Bin #2', capacity=100.0, status='empty', cleaning_type='24_hour'),
                CleaningBin(name='12-Hour Cleaning Bin #1', capacity=75.0, status='empty', cleaning_type='12_hour'),
                CleaningBin(name='12-Hour Cleaning Bin #2', capacity=75.0, status='empty', cleaning_type='12_hour')
            ]
            db.session.add_all(cleaning_bins)
            db.session.commit()
        
        # Create 4 storage areas as requested
        from models import StorageArea
        if not db.session.query(StorageArea).first():
            storage_areas = [
                StorageArea(name='Storage Area A', capacity_kg=5000.0, location='Main Warehouse Section A'),
                StorageArea(name='Storage Area B', capacity_kg=4000.0, location='Main Warehouse Section B'),
                StorageArea(name='Storage Area C', capacity_kg=3500.0, location='Secondary Warehouse Section A'),
                StorageArea(name='Storage Area D', capacity_kg=4500.0, location='Secondary Warehouse Section B')
            ]
            db.session.add_all(storage_areas)
            db.session.commit()
        
        # Create B1 scale machine
        from models import B1ScaleCleaning
        if not db.session.query(B1ScaleCleaning).first():
            b1_machine = B1ScaleCleaning(
                machine_name='B1 Scale',
                cleaning_frequency_minutes=60,
                last_cleaned=datetime.utcnow(),
                next_cleaning_due=datetime.utcnow() + timedelta(minutes=60),
                status='completed'
            )
            db.session.add(b1_machine)
            db.session.commit()
        
        # Create sample production machines
        from models import ProductionMachine
        if not db.session.query(ProductionMachine).first():
            sample_machines = [
                ProductionMachine(name='Drum Shield #1', machine_type='drum_shield', process_step='precleaning', location='Precleaning Area A', cleaning_frequency_hours=3),
                ProductionMachine(name='Magnet Separator #1', machine_type='magnet', process_step='precleaning', location='Precleaning Area B', cleaning_frequency_hours=3),
                ProductionMachine(name='24h Cleaning Machine #1', machine_type='cleaner', process_step='cleaning_24h', location='Cleaning Bay 1', cleaning_frequency_hours=3),
                ProductionMachine(name='24h Cleaning Machine #2', machine_type='cleaner', process_step='cleaning_24h', location='Cleaning Bay 2', cleaning_frequency_hours=3),
                ProductionMachine(name='12h Cleaning Machine #1', machine_type='cleaner', process_step='cleaning_12h', location='Final Cleaning Area', cleaning_frequency_hours=3),
                ProductionMachine(name='Grinding Machine #1', machine_type='grinder', process_step='grinding', location='Grinding Hall A', cleaning_frequency_hours=3),
                ProductionMachine(name='Grinding Machine #2', machine_type='grinder', process_step='grinding', location='Grinding Hall B', cleaning_frequency_hours=3),
                ProductionMachine(name='Packing Machine #1', machine_type='packer', process_step='packing', location='Packing Area A', cleaning_frequency_hours=4),
                ProductionMachine(name='Packing Machine #2', machine_type='packer', process_step='packing', location='Packing Area B', cleaning_frequency_hours=4)
            ]
            db.session.add_all(sample_machines)
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing sample data: {e}")
        # Continue with basic setup even if sample data fails
        pass

# Initialize the app context and create tables
with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all tables
    db.create_all()
    init_sample_data()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
