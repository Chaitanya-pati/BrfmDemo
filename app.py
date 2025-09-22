
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
        from models import GodownType, Godown, PrecleaningBin, Supplier, Product, Customer, ShallowsMaster
        from datetime import timedelta, datetime
        
        # Create godown types
        if not db.session.query(GodownType).first():
            mill_type = GodownType()
            mill_type.name = 'Mill'
            mill_type.description = 'Regular mill quality wheat'
            
            low_mill_type = GodownType()
            low_mill_type.name = 'Low Mill'
            low_mill_type.description = 'Lower quality wheat'
            
            hd_type = GodownType()
            hd_type.name = 'HD'
            hd_type.description = 'High density wheat'
            
            db.session.add_all([mill_type, low_mill_type, hd_type])
            db.session.commit()
        
        # Create sample godowns
        if not db.session.query(Godown).first():
            godown1 = Godown()
            godown1.name = 'Godown A'
            godown1.type_id = 1
            godown1.capacity = 100.0
            
            godown2 = Godown()
            godown2.name = 'Godown B'
            godown2.type_id = 2
            godown2.capacity = 150.0
            
            godown3 = Godown()
            godown3.name = 'Godown C'
            godown3.type_id = 3
            godown3.capacity = 200.0
            
            db.session.add_all([godown1, godown2, godown3])
            db.session.commit()
        
        # Create sample precleaning bins
        if not db.session.query(PrecleaningBin).first():
            bin1 = PrecleaningBin()
            bin1.name = 'Pre-cleaning Bin 1'
            bin1.capacity = 50.0
            
            bin2 = PrecleaningBin()
            bin2.name = 'Pre-cleaning Bin 2'
            bin2.capacity = 75.0
            
            bin3 = PrecleaningBin()
            bin3.name = 'Pre-cleaning Bin 3'
            bin3.capacity = 60.0
            
            db.session.add_all([bin1, bin2, bin3])
            db.session.commit()
        
        # Create sample suppliers
        if not db.session.query(Supplier).first():
            supplier1 = Supplier()
            supplier1.company_name = 'ABC Wheat Suppliers'
            supplier1.contact_person = 'John Doe'
            supplier1.phone = '9876543210'
            supplier1.city = 'Delhi'
            
            supplier2 = Supplier()
            supplier2.company_name = 'XYZ Grain Traders'
            supplier2.contact_person = 'Jane Smith'
            supplier2.phone = '9876543211'
            supplier2.city = 'Mumbai'
            
            db.session.add_all([supplier1, supplier2])
            db.session.commit()
        
        # Create sample products
        if not db.session.query(Product).first():
            maida = Product()
            maida.name = 'Maida'
            maida.category = 'Main Product'
            maida.description = 'Refined wheat flour'
            
            suji = Product()
            suji.name = 'Suji'
            suji.category = 'Main Product'
            suji.description = 'Semolina'
            
            chakki_ata = Product()
            chakki_ata.name = 'Chakki Ata'
            chakki_ata.category = 'Main Product'
            chakki_ata.description = 'Whole wheat flour'
            
            bran = Product()
            bran.name = 'Bran'
            bran.category = 'Bran'
            bran.description = 'Wheat bran'
            
            db.session.add_all([maida, suji, chakki_ata, bran])
            db.session.commit()
        
        # Create sample customers
        if not db.session.query(Customer).first():
            customer1 = Customer()
            customer1.company_name = 'ABC Bakery'
            customer1.contact_person = 'Ram Kumar'
            customer1.phone = '9876543220'
            customer1.city = 'Delhi'
            
            customer2 = Customer()
            customer2.company_name = 'XYZ Food Products'
            customer2.contact_person = 'Shyam Gupta'
            customer2.phone = '9876543221'
            customer2.city = 'Mumbai'
            
            db.session.add_all([customer1, customer2])
            db.session.commit()
        
        # Create cleaning bins for 24h and 12h processes
        from models import CleaningBin
        if not db.session.query(CleaningBin).first():
            bin1 = CleaningBin()
            bin1.name = '24-Hour Cleaning Bin #1'
            bin1.capacity = 100.0
            bin1.status = 'empty'
            bin1.cleaning_type = '24_hour'
            
            bin2 = CleaningBin()
            bin2.name = '24-Hour Cleaning Bin #2'
            bin2.capacity = 100.0
            bin2.status = 'empty'
            bin2.cleaning_type = '24_hour'
            
            bin3 = CleaningBin()
            bin3.name = '12-Hour Cleaning Bin #1'
            bin3.capacity = 75.0
            bin3.status = 'empty'
            bin3.cleaning_type = '12_hour'
            
            bin4 = CleaningBin()
            bin4.name = '12-Hour Cleaning Bin #2'
            bin4.capacity = 75.0
            bin4.status = 'empty'
            bin4.cleaning_type = '12_hour'
            
            db.session.add_all([bin1, bin2, bin3, bin4])
            db.session.commit()
        
        # Create 4 storage areas as requested
        from models import StorageArea
        if not db.session.query(StorageArea).first():
            storage1 = StorageArea()
            storage1.name = 'Storage Area A'
            storage1.capacity_kg = 5000.0
            storage1.location = 'Main Warehouse Section A'
            
            storage2 = StorageArea()
            storage2.name = 'Storage Area B'
            storage2.capacity_kg = 4000.0
            storage2.location = 'Main Warehouse Section B'
            
            storage3 = StorageArea()
            storage3.name = 'Storage Area C'
            storage3.capacity_kg = 3500.0
            storage3.location = 'Secondary Warehouse Section A'
            
            storage4 = StorageArea()
            storage4.name = 'Storage Area D'
            storage4.capacity_kg = 4500.0
            storage4.location = 'Secondary Warehouse Section B'
            
            db.session.add_all([storage1, storage2, storage3, storage4])
            db.session.commit()
        
        # Create sample shallows
        if not db.session.query(ShallowsMaster).first():
            shallow1 = ShallowsMaster()
            shallow1.name = 'Shallow Tank A'
            shallow1.capacity_kg = 2000.0
            shallow1.location = 'Main Processing Area'
            
            shallow2 = ShallowsMaster()
            shallow2.name = 'Shallow Tank B'
            shallow2.capacity_kg = 1500.0
            shallow2.location = 'Main Processing Area'
            
            shallow3 = ShallowsMaster()
            shallow3.name = 'Shallow Tank C'
            shallow3.capacity_kg = 1800.0
            shallow3.location = 'Secondary Processing Area'
            
            db.session.add_all([shallow1, shallow2, shallow3])
            db.session.commit()
        
        # Create B1 scale machine
        from models import B1ScaleCleaning
        if not db.session.query(B1ScaleCleaning).first():
            b1_machine = B1ScaleCleaning()
            b1_machine.machine_name = 'B1 Scale'
            b1_machine.cleaning_frequency_minutes = 60
            b1_machine.last_cleaned = datetime.utcnow()
            b1_machine.next_cleaning_due = datetime.utcnow() + timedelta(minutes=60)
            b1_machine.status = 'completed'
            
            db.session.add(b1_machine)
            db.session.commit()
        
        # ProductionMachine initialization removed - production functionality deleted
            
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
