
from app import app, db
from models import (
    Supplier, GodownType, Godown, PrecleaningBin, Product, Customer, 
    CleaningMachine, CleaningBin, StorageArea, User
)
from datetime import datetime

def add_master_data():
    """Add basic master data to all tables"""
    with app.app_context():
        try:
            print("Adding master data...")
            
            # 1. Add Godown Types
            print("Adding godown types...")
            if not GodownType.query.first():
                godown_types = [
                    GodownType(name='Mill', description='High quality mill wheat'),
                    GodownType(name='Low Mill', description='Lower grade mill wheat'),
                    GodownType(name='HD', description='High density wheat'),
                    GodownType(name='Durum', description='Durum wheat variety')
                ]
                db.session.add_all(godown_types)
                db.session.commit()
                print("✓ Godown types added")
            
            # 2. Add Godowns
            print("Adding godowns...")
            if not Godown.query.first():
                godowns = [
                    Godown(name='Godown A-1', type_id=1, capacity=200000.0, current_stock=150000.0),
                    Godown(name='Godown A-2', type_id=1, capacity=250000.0, current_stock=180000.0),
                    Godown(name='Godown B-1', type_id=2, capacity=180000.0, current_stock=120000.0),
                    Godown(name='Godown B-2', type_id=2, capacity=200000.0, current_stock=95000.0),
                    Godown(name='Godown C-1', type_id=3, capacity=300000.0, current_stock=245000.0),
                    Godown(name='Godown C-2', type_id=3, capacity=280000.0, current_stock=210000.0),
                    Godown(name='Godown D-1', type_id=4, capacity=150000.0, current_stock=85000.0),
                    Godown(name='Emergency Storage', type_id=1, capacity=100000.0, current_stock=45000.0)
                ]
                db.session.add_all(godowns)
                db.session.commit()
                print("✓ Godowns added")
            
            # 3. Add Pre-cleaning Bins
            print("Adding pre-cleaning bins...")
            if not PrecleaningBin.query.first():
                precleaning_bins = [
                    PrecleaningBin(name='Pre-cleaning Bin 1', capacity=80000.0, current_stock=65000.0),
                    PrecleaningBin(name='Pre-cleaning Bin 2', capacity=75000.0, current_stock=45000.0),
                    PrecleaningBin(name='Pre-cleaning Bin 3', capacity=90000.0, current_stock=72000.0),
                    PrecleaningBin(name='Pre-cleaning Bin 4', capacity=85000.0, current_stock=38000.0),
                    PrecleaningBin(name='Pre-cleaning Bin 5', capacity=70000.0, current_stock=55000.0)
                ]
                db.session.add_all(precleaning_bins)
                db.session.commit()
                print("✓ Pre-cleaning bins added")
            
            # 4. Add Cleaning Bins
            print("Adding cleaning bins...")
            if not CleaningBin.query.first():
                cleaning_bins = [
                    CleaningBin(
                        name='24-Hour Cleaning Bin 1',
                        capacity=60000.0,
                        current_stock=45000.0,
                        status='occupied',
                        location='Cleaning Area A',
                        cleaning_type='24_hour'
                    ),
                    CleaningBin(
                        name='24-Hour Cleaning Bin 2',
                        capacity=65000.0,
                        current_stock=0.0,
                        status='empty',
                        location='Cleaning Area A',
                        cleaning_type='24_hour'
                    ),
                    CleaningBin(
                        name='12-Hour Cleaning Bin 1',
                        capacity=50000.0,
                        current_stock=32000.0,
                        status='cleaning',
                        location='Cleaning Area B',
                        cleaning_type='12_hour'
                    ),
                    CleaningBin(
                        name='12-Hour Cleaning Bin 2',
                        capacity=55000.0,
                        current_stock=0.0,
                        status='empty',
                        location='Cleaning Area B',
                        cleaning_type='12_hour'
                    )
                ]
                db.session.add_all(cleaning_bins)
                db.session.commit()
                print("✓ Cleaning bins added")
            
            # 5. Add Suppliers
            print("Adding suppliers...")
            if not Supplier.query.first():
                suppliers = [
                    Supplier(
                        company_name='Punjab Wheat Traders',
                        contact_person='Rajesh Kumar',
                        phone='9876543210',
                        address='Sector 22, Industrial Area',
                        city='Ludhiana',
                        state='Punjab',
                        postal_code='141001'
                    ),
                    Supplier(
                        company_name='Haryana Grain Supply Co.',
                        contact_person='Suresh Malik',
                        phone='9876543211',
                        address='Plot 45, Grain Market',
                        city='Karnal',
                        state='Haryana',
                        postal_code='132001'
                    ),
                    Supplier(
                        company_name='UP Wheat Corporation',
                        contact_person='Ramesh Gupta',
                        phone='9876543212',
                        address='Mandi Road, Block A',
                        city='Meerut',
                        state='Uttar Pradesh',
                        postal_code='250001'
                    )
                ]
                db.session.add_all(suppliers)
                db.session.commit()
                print("✓ Suppliers added")
            
            # 6. Add Customers
            print("Adding customers...")
            if not Customer.query.first():
                customers = [
                    Customer(
                        company_name='Mumbai Bakery Solutions',
                        contact_person='Amit Patel',
                        phone='9876543220',
                        email='amit@mumbaibakery.com',
                        address='Shop 15, Linking Road',
                        city='Mumbai',
                        state='Maharashtra',
                        postal_code='400050'
                    ),
                    Customer(
                        company_name='Delhi Bread Company',
                        contact_person='Rahul Sharma',
                        phone='9876543221',
                        email='rahul@delhibread.com',
                        address='Block B-12, Mayapuri',
                        city='Delhi',
                        state='Delhi',
                        postal_code='110064'
                    ),
                    Customer(
                        company_name='Pune Food Industries',
                        contact_person='Sachin Deshmukh',
                        phone='9876543222',
                        email='sachin@punefood.com',
                        address='Plot 34, MIDC Area',
                        city='Pune',
                        state='Maharashtra',
                        postal_code='411019'
                    )
                ]
                db.session.add_all(customers)
                db.session.commit()
                print("✓ Customers added")
            
            # 7. Add Products
            print("Adding products...")
            if not Product.query.first():
                products = [
                    Product(name='Maida', category='Main Product', description='Refined wheat flour - Premium quality'),
                    Product(name='Suji', category='Main Product', description='Semolina - Coarse wheat flour'),
                    Product(name='Chakki Atta', category='Main Product', description='Whole wheat flour - Stone ground'),
                    Product(name='Rawa', category='Main Product', description='Fine semolina'),
                    Product(name='Daliya', category='Main Product', description='Broken wheat'),
                    Product(name='Wheat Bran', category='Bran', description='Wheat bran by-product'),
                    Product(name='Fine Bran', category='Bran', description='Fine wheat bran'),
                    Product(name='Coarse Bran', category='Bran', description='Coarse wheat bran')
                ]
                db.session.add_all(products)
                db.session.commit()
                print("✓ Products added")
            
            # 8. Add Cleaning Machines
            print("Adding cleaning machines...")
            if not CleaningMachine.query.first():
                cleaning_machines = [
                    CleaningMachine(
                        name='Drum Shield Machine 1',
                        machine_type='drum_shield',
                        cleaning_frequency_hours=3,

        # Create Cleaning Bins
        if CleaningBin.query.count() == 0:
            print("Creating cleaning bins...")
            cleaning_bins = [
                CleaningBin(
                    name='Cleaning Bin #1',
                    capacity=50.0,
                    current_stock=0.0,
                    status='available',
                    location='Cleaning Area A'
                ),
                CleaningBin(
                    name='Cleaning Bin #2', 
                    capacity=50.0,
                    current_stock=0.0,
                    status='available',
                    location='Cleaning Area B'
                ),
                CleaningBin(
                    name='Cleaning Bin #3',
                    capacity=75.0,
                    current_stock=0.0,
                    status='available',
                    location='Cleaning Area C'
                ),
                CleaningBin(
                    name='Cleaning Bin #4',
                    capacity=75.0,
                    current_stock=0.0,
                    status='available',
                    location='Cleaning Area D'
                )
            ]
            
            for bin in cleaning_bins:
                db.session.add(bin)
            
            print(f"Created {len(cleaning_bins)} cleaning bins")


                        location='Pre-cleaning Area A',
                        last_cleaned=datetime.now()
                    ),
                    CleaningMachine(
                        name='Magnet Separator 1',
                        machine_type='magnet',
                        cleaning_frequency_hours=4,
                        location='Pre-cleaning Area B',
                        last_cleaned=datetime.now()
                    ),
                    CleaningMachine(
                        name='Grain Separator 1',
                        machine_type='separator',
                        cleaning_frequency_hours=2,
                        location='Cleaning Section 1',
                        last_cleaned=datetime.now()
                    ),
                    CleaningMachine(
                        name='Grinding Mill 1',
                        machine_type='grinding',
                        cleaning_frequency_hours=1,
                        location='Production Floor A',
                        last_cleaned=datetime.now()
                    ),
                    CleaningMachine(
                        name='Grinding Mill 2',
                        machine_type='grinding',
                        cleaning_frequency_hours=1,
                        location='Production Floor B',
                        last_cleaned=datetime.now()
                    )
                ]
                db.session.add_all(cleaning_machines)
                db.session.commit()
                print("✓ Cleaning machines added")
            
            # 9. Add Storage Areas
            print("Adding storage areas...")
            if not StorageArea.query.first():
                storage_areas = [
                    StorageArea(name='Production Storage 1', capacity_kg=50000, current_stock_kg=32500, location='Floor A'),
                    StorageArea(name='Production Storage 2', capacity_kg=60000, current_stock_kg=45200, location='Floor B'),
                    StorageArea(name='Packing Area 1', capacity_kg=30000, current_stock_kg=18500, location='Packing Floor'),
                    StorageArea(name='Quality Hold Area', capacity_kg=20000, current_stock_kg=8900, location='QC Section')
                ]
                db.session.add_all(storage_areas)
                db.session.commit()
                print("✓ Storage areas added")
            
            # 10. Add Users
            print("Adding users...")
            if not User.query.first():
                users = [
                    User(username='admin', role='admin', phone='9876543400'),
                    User(username='production_manager', role='production_manager', phone='9876543401'),
                    User(username='operator1', role='operator', phone='9876543402'),
                    User(username='operator2', role='operator', phone='9876543403'),
                    User(username='lab_instructor1', role='lab_instructor', phone='9876543404'),
                    User(username='lab_instructor2', role='lab_instructor', phone='9876543405')
                ]
                db.session.add_all(users)
                db.session.commit()
                print("✓ Users added")
            
            print("\n✅ All master data added successfully!")
            print("Summary:")
            print(f"- Godown Types: {GodownType.query.count()}")
            print(f"- Godowns: {Godown.query.count()}")
            print(f"- Pre-cleaning Bins: {PrecleaningBin.query.count()}")
            print(f"- Cleaning Bins: {CleaningBin.query.count()}")
            print(f"- Suppliers: {Supplier.query.count()}")
            print(f"- Customers: {Customer.query.count()}")
            print(f"- Products: {Product.query.count()}")
            print(f"- Cleaning Machines: {CleaningMachine.query.count()}")
            print(f"- Storage Areas: {StorageArea.query.count()}")
            print(f"- Users: {User.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding master data: {e}")
            raise e

if __name__ == '__main__':
    add_master_data()
