
from app import app, db
from models import *
from datetime import datetime, timedelta
import random

def add_sample_data():
    with app.app_context():
        try:
            # Add Suppliers
            if not Supplier.query.first():
                suppliers = [
                    Supplier(company_name='ABC Wheat Suppliers', contact_person='John Doe', phone='9876543210', city='Delhi', address='123 Main St, Delhi'),
                    Supplier(company_name='XYZ Grain Traders', contact_person='Jane Smith', phone='9876543211', city='Mumbai', address='456 Market St, Mumbai'),
                    Supplier(company_name='Prime Agro Products', contact_person='Ram Singh', phone='9876543212', city='Ludhiana', address='789 Farm Road, Ludhiana'),
                    Supplier(company_name='Golden Grain Co.', contact_person='Rajesh Kumar', phone='9876543213', city='Amritsar', address='321 Grain Market, Amritsar')
                ]
                for supplier in suppliers:
                    db.session.add(supplier)
                db.session.commit()
                print("✓ Suppliers added")

            # Add Customers
            if not Customer.query.first():
                customers = [
                    Customer(company_name='ABC Bakery', contact_person='Ram Kumar', phone='9876543220', city='Delhi', address='100 Bakery Lane, Delhi'),
                    Customer(company_name='XYZ Food Products', contact_person='Shyam Gupta', phone='9876543221', city='Mumbai', address='200 Food St, Mumbai'),
                    Customer(company_name='Modern Mills', contact_person='Suresh Sharma', phone='9876543222', city='Bangalore', address='300 Industrial Area, Bangalore'),
                    Customer(company_name='Royal Flour Mills', contact_person='Vikash Patel', phone='9876543223', city='Ahmedabad', address='400 Mill Road, Ahmedabad')
                ]
                for customer in customers:
                    db.session.add(customer)
                db.session.commit()
                print("✓ Customers added")

            # Add Products
            if not Product.query.first():
                products = [
                    Product(name='Maida', category='Main Product', description='Refined wheat flour', unit='kg', standard_price=45.0),
                    Product(name='Suji', category='Main Product', description='Semolina', unit='kg', standard_price=50.0),
                    Product(name='Chakki Ata', category='Main Product', description='Whole wheat flour', unit='kg', standard_price=40.0),
                    Product(name='Tandoori Ata', category='Main Product', description='Special wheat flour for tandoor', unit='kg', standard_price=42.0),
                    Product(name='Bran', category='By-product', description='Wheat bran', unit='kg', standard_price=20.0),
                    Product(name='Fine Flour', category='Main Product', description='Fine quality flour', unit='kg', standard_price=48.0)
                ]
                for product in products:
                    db.session.add(product)
                db.session.commit()
                print("✓ Products added")

            # Add GodownTypes
            if not GodownType.query.first():
                godown_types = [
                    GodownType(name='Mill', description='Regular mill quality wheat'),
                    GodownType(name='Low Mill', description='Lower quality wheat'),
                    GodownType(name='HD', description='High density wheat'),
                    GodownType(name='Premium', description='Premium quality wheat')
                ]
                for gt in godown_types:
                    db.session.add(gt)
                db.session.commit()
                print("✓ Godown Types added")

            # Add Godowns
            if not Godown.query.first():
                godowns = [
                    Godown(name='Godown A', type_id=1, capacity=1000.0, current_stock=750.0, location='Section A'),
                    Godown(name='Godown B', type_id=2, capacity=800.0, current_stock=600.0, location='Section B'),
                    Godown(name='Godown C', type_id=3, capacity=1200.0, current_stock=900.0, location='Section C'),
                    Godown(name='Godown D', type_id=1, capacity=1500.0, current_stock=1100.0, location='Section D'),
                    Godown(name='Godown E', type_id=4, capacity=500.0, current_stock=200.0, location='Premium Section')
                ]
                for godown in godowns:
                    db.session.add(godown)
                db.session.commit()
                print("✓ Godowns added")

            # Add PrecleaningBins
            if not PrecleaningBin.query.first():
                precleaning_bins = [
                    PrecleaningBin(name='Pre-cleaning Bin 1', capacity=200.0, current_stock=150.0, location='Area A'),
                    PrecleaningBin(name='Pre-cleaning Bin 2', capacity=250.0, current_stock=180.0, location='Area B'),
                    PrecleaningBin(name='Pre-cleaning Bin 3', capacity=300.0, current_stock=220.0, location='Area C'),
                    PrecleaningBin(name='Pre-cleaning Bin 4', capacity=200.0, current_stock=100.0, location='Area D')
                ]
                for bin in precleaning_bins:
                    db.session.add(bin)
                db.session.commit()
                print("✓ Precleaning Bins added")

            # Add CleaningBins
            if not CleaningBin.query.first():
                cleaning_bins = [
                    CleaningBin(name='24-Hour Cleaning Bin #1', capacity=150.0, current_stock=0.0, status='empty', cleaning_type='24_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #2', capacity=150.0, current_stock=0.0, status='empty', cleaning_type='24_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #1', capacity=100.0, current_stock=0.0, status='empty', cleaning_type='12_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #2', capacity=100.0, current_stock=0.0, status='empty', cleaning_type='12_hour')
                ]
                for bin in cleaning_bins:
                    db.session.add(bin)
                db.session.commit()
                print("✓ Cleaning Bins added")

            # Add StorageAreas
            if not StorageArea.query.first():
                storage_areas = [
                    StorageArea(name='Storage Area A', capacity_kg=5000.0, current_stock_kg=2500.0, location='Main Warehouse Section A'),
                    StorageArea(name='Storage Area B', capacity_kg=4000.0, current_stock_kg=2000.0, location='Main Warehouse Section B'),
                    StorageArea(name='Storage Area C', capacity_kg=3500.0, current_stock_kg=1750.0, location='Secondary Warehouse Section A'),
                    StorageArea(name='Storage Area D', capacity_kg=4500.0, current_stock_kg=2250.0, location='Secondary Warehouse Section B')
                ]
                for area in storage_areas:
                    db.session.add(area)
                db.session.commit()
                print("✓ Storage Areas added")

            # Add Vehicles
            if not Vehicle.query.first():
                vehicles = [
                    Vehicle(vehicle_number='HR-01-AB-1234', supplier_id=1, driver_name='Ramesh Kumar', driver_phone='9876543230', 
                           arrival_time=datetime.now() - timedelta(hours=2), status='approved', final_weight=2500.0),
                    Vehicle(vehicle_number='PB-02-CD-5678', supplier_id=2, driver_name='Suresh Singh', driver_phone='9876543231', 
                           arrival_time=datetime.now() - timedelta(hours=1), status='quality_check', final_weight=3000.0),
                    Vehicle(vehicle_number='UP-03-EF-9012', supplier_id=3, driver_name='Mohan Lal', driver_phone='9876543232', 
                           arrival_time=datetime.now() - timedelta(minutes=30), status='pending', final_weight=2800.0)
                ]
                for vehicle in vehicles:
                    db.session.add(vehicle)
                db.session.commit()
                print("✓ Vehicles added")

            # Add QualityTests
            if not QualityTest.query.first():
                quality_tests = [
                    QualityTest(vehicle_id=1, sample_bags_tested=5, total_bags=50, category_assigned='Premium', 
                               moisture_content=12.5, lab_instructor='Dr. Sharma', approved=True),
                    QualityTest(vehicle_id=2, sample_bags_tested=3, total_bags=60, category_assigned='Standard', 
                               moisture_content=13.2, lab_instructor='Dr. Patel', approved=True)
                ]
                for test in quality_tests:
                    db.session.add(test)
                db.session.commit()
                print("✓ Quality Tests added")

            # Add ProductionOrders
            if not ProductionOrder.query.first():
                production_orders = [
                    ProductionOrder(order_number='ORD-2025-001', product_id=1, customer_id=1, quantity=1000.0, status='completed', 
                                   priority='high', created_by='Manager1', target_completion_date=datetime.now() + timedelta(days=2)),
                    ProductionOrder(order_number='ORD-2025-002', product_id=2, customer_id=2, quantity=800.0, status='in_progress', 
                                   priority='normal', created_by='Manager2', target_completion_date=datetime.now() + timedelta(days=3)),
                    ProductionOrder(order_number='ORD-2025-003', product_id=3, customer_id=3, quantity=1200.0, status='pending', 
                                   priority='low', created_by='Manager1', target_completion_date=datetime.now() + timedelta(days=5))
                ]
                for order in production_orders:
                    db.session.add(order)
                db.session.commit()
                print("✓ Production Orders added")

            # Add ProductionPlans
            if not ProductionPlan.query.first():
                production_plans = [
                    ProductionPlan(order_id=1, plan_date=datetime.now().date(), target_quantity=1000.0, 
                                  status='executed', created_by='Planner1'),
                    ProductionPlan(order_id=2, plan_date=datetime.now().date(), target_quantity=800.0, 
                                  status='approved', created_by='Planner2'),
                    ProductionPlan(order_id=3, plan_date=datetime.now().date() + timedelta(days=1), target_quantity=1200.0, 
                                  status='draft', created_by='Planner1')
                ]
                for plan in production_plans:
                    db.session.add(plan)
                db.session.commit()
                print("✓ Production Plans added")

            # Add ProductionJobs
            if not ProductionJobNew.query.first():
                production_jobs = [
                    ProductionJobNew(job_number='JOB-001-TRANSFER', order_id=1, plan_id=1, stage='transfer', 
                                    status='completed', started_by='Operator1', completed_by='Operator1',
                                    started_at=datetime.now() - timedelta(hours=5), completed_at=datetime.now() - timedelta(hours=4)),
                    ProductionJobNew(job_number='JOB-001-CLEANING24H', order_id=1, plan_id=1, stage='cleaning_24h', 
                                    status='completed', started_by='Operator2', completed_by='Operator2',
                                    started_at=datetime.now() - timedelta(hours=4), completed_at=datetime.now() - timedelta(hours=3)),
                    ProductionJobNew(job_number='JOB-002-TRANSFER', order_id=2, plan_id=2, stage='transfer', 
                                    status='in_progress', started_by='Operator3',
                                    started_at=datetime.now() - timedelta(hours=1))
                ]
                for job in production_jobs:
                    db.session.add(job)
                db.session.commit()
                print("✓ Production Jobs added")

            # Add FinishedGoods
            if not FinishedGoods.query.first():
                finished_goods = [
                    FinishedGoods(order_id=1, product_id=1, quantity=950.0, storage_type='bags', 
                                 bag_weight=50.0, bag_count=19, batch_number='BATCH-ORD-2025-001-20250906'),
                    FinishedGoods(order_id=1, product_id=5, quantity=50.0, storage_type='bulk', 
                                 batch_number='BATCH-ORD-2025-001-BRAN-20250906')
                ]
                for fg in finished_goods:
                    db.session.add(fg)
                db.session.commit()
                print("✓ Finished Goods added")

            # Add SalesDispatch
            if not SalesDispatch.query.first():
                sales_dispatches = [
                    SalesDispatch(order_id=1, customer_id=1, product_id=1, quantity=500.0, 
                                 dispatch_date=datetime.now().date(), vehicle_number='HR-01-XY-9999', 
                                 driver_name='Delivery Driver', status='dispatched')
                ]
                for dispatch in sales_dispatches:
                    db.session.add(dispatch)
                db.session.commit()
                print("✓ Sales Dispatches added")

            # Add ProductionMachines
            if not ProductionMachine.query.first():
                production_machines = [
                    ProductionMachine(name='Drum Shield #1', machine_type='drum_shield', process_step='precleaning', 
                                     location='Precleaning Area A', cleaning_frequency_hours=3),
                    ProductionMachine(name='24h Cleaning Machine #1', machine_type='cleaner', process_step='cleaning_24h', 
                                     location='Cleaning Bay 1', cleaning_frequency_hours=3),
                    ProductionMachine(name='Grinding Machine #1', machine_type='grinder', process_step='grinding', 
                                     location='Grinding Hall A', cleaning_frequency_hours=3),
                    ProductionMachine(name='Packing Machine #1', machine_type='packer', process_step='packing', 
                                     location='Packing Area A', cleaning_frequency_hours=4)
                ]
                for machine in production_machines:
                    db.session.add(machine)
                db.session.commit()
                print("✓ Production Machines added")

            # Add CleaningMachines
            if not CleaningMachine.query.first():
                cleaning_machines = [
                    CleaningMachine(name='Cleaning Machine A', machine_type='industrial_cleaner', 
                                   cleaning_frequency_hours=2, last_cleaned=datetime.now() - timedelta(hours=1)),
                    CleaningMachine(name='Cleaning Machine B', machine_type='drum_cleaner', 
                                   cleaning_frequency_hours=3, last_cleaned=datetime.now() - timedelta(hours=2))
                ]
                for machine in cleaning_machines:
                    db.session.add(machine)
                db.session.commit()
                print("✓ Cleaning Machines added")

            print("\n🎉 All sample data has been successfully added to all tables!")
            print("You can now start using the application with pre-populated data.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding sample data: {str(e)}")

if __name__ == '__main__':
    add_sample_data()
