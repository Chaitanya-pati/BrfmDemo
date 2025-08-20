
from datetime import datetime, timedelta
import random
from app import app, db
from models import (
    Supplier, GodownType, Godown, PrecleaningBin, Product, Customer, Vehicle,
    QualityTest, Transfer, CleaningMachine, CleaningLog, ProductionOrder,
    ProductionPlan, ProductionPlanItem, FinishedGoodsStorage, FinishedGoods,
    SalesOrder, SalesOrderItem, DispatchVehicle, Dispatch, SalesDispatch,
    DispatchItem, User, CleaningReminder, ProductionJobNew, ProductionTransfer,
    CleaningBin, CleaningProcess, GrindingProcess, ProductOutput, PackingProcess,
    StorageArea, StorageTransfer, ProcessReminder
)

def populate_dummy_data():
    """Populate all tables with comprehensive dummy data"""
    with app.app_context():
        try:
            # Clear existing data
            print("Clearing existing data...")
            db.session.query(ProcessReminder).delete()
            db.session.query(StorageTransfer).delete()
            db.session.query(ProductOutput).delete()
            db.session.query(PackingProcess).delete()
            db.session.query(GrindingProcess).delete()
            db.session.query(CleaningProcess).delete()
            db.session.query(ProductionTransfer).delete()
            db.session.query(ProductionJobNew).delete()
            db.session.query(CleaningReminder).delete()
            db.session.query(DispatchItem).delete()
            db.session.query(Dispatch).delete()
            db.session.query(SalesDispatch).delete()
            db.session.query(SalesOrderItem).delete()
            db.session.query(SalesOrder).delete()
            db.session.query(FinishedGoods).delete()
            db.session.query(ProductionPlanItem).delete()
            db.session.query(ProductionPlan).delete()
            db.session.query(ProductionOrder).delete()
            db.session.query(CleaningLog).delete()
            db.session.query(Transfer).delete()
            db.session.query(QualityTest).delete()
            db.session.query(Vehicle).delete()
            db.session.commit()

            # 1. Create Suppliers
            print("Creating suppliers...")
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
                ),
                Supplier(
                    company_name='Delhi Grain Suppliers',
                    contact_person='Vikash Singh',
                    phone='9876543213',
                    address='Azadpur Mandi',
                    city='Delhi',
                    state='Delhi',
                    postal_code='110033'
                ),
                Supplier(
                    company_name='Rajasthan Wheat Hub',
                    contact_person='Mohan Lal',
                    phone='9876543214',
                    address='Grain Market Complex',
                    city='Kota',
                    state='Rajasthan',
                    postal_code='324001'
                )
            ]
            db.session.add_all(suppliers)
            db.session.commit()

            # 2. Create Godown Types
            print("Creating godown types...")
            godown_types = [
                GodownType(name='Mill', description='High quality mill wheat'),
                GodownType(name='Low Mill', description='Lower grade mill wheat'),
                GodownType(name='HD', description='High density wheat'),
                GodownType(name='Durum', description='Durum wheat variety')
            ]
            db.session.add_all(godown_types)
            db.session.commit()

            # 3. Create Godowns
            print("Creating godowns...")
            godowns = [
                Godown(name='Godown A-1', type_id=1, capacity=200.0, current_stock=150.5),
                Godown(name='Godown A-2', type_id=1, capacity=250.0, current_stock=180.2),
                Godown(name='Godown B-1', type_id=2, capacity=180.0, current_stock=120.8),
                Godown(name='Godown B-2', type_id=2, capacity=200.0, current_stock=95.3),
                Godown(name='Godown C-1', type_id=3, capacity=300.0, current_stock=245.7),
                Godown(name='Godown C-2', type_id=3, capacity=280.0, current_stock=210.4),
                Godown(name='Godown D-1', type_id=4, capacity=150.0, current_stock=85.6),
                Godown(name='Emergency Storage', type_id=1, capacity=100.0, current_stock=45.2)
            ]
            db.session.add_all(godowns)
            db.session.commit()

            # 4. Create Precleaning Bins
            print("Creating precleaning bins...")
            precleaning_bins = [
                PrecleaningBin(name='Pre-cleaning Bin 1', capacity=80.0, current_stock=65.5),
                PrecleaningBin(name='Pre-cleaning Bin 2', capacity=75.0, current_stock=45.8),
                PrecleaningBin(name='Pre-cleaning Bin 3', capacity=90.0, current_stock=72.3),
                PrecleaningBin(name='Pre-cleaning Bin 4', capacity=85.0, current_stock=38.7),
                PrecleaningBin(name='Pre-cleaning Bin 5', capacity=70.0, current_stock=55.2)
            ]
            db.session.add_all(precleaning_bins)
            db.session.commit()

            # 5. Create Products
            print("Creating products...")
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

            # 6. Create Customers
            print("Creating customers...")
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
                ),
                Customer(
                    company_name='Chennai Flour Mills',
                    contact_person='Ravi Kumar',
                    phone='9876543223',
                    email='ravi@chennaiflour.com',
                    address='Industrial Estate, Ambattur',
                    city='Chennai',
                    state='Tamil Nadu',
                    postal_code='600058'
                ),
                Customer(
                    company_name='Kolkata Bakery Hub',
                    contact_person='Debashis Roy',
                    phone='9876543224',
                    email='debashis@kolkatabakery.com',
                    address='Sector V, Salt Lake',
                    city='Kolkata',
                    state='West Bengal',
                    postal_code='700091'
                )
            ]
            db.session.add_all(customers)
            db.session.commit()

            # 7. Create Vehicles
            print("Creating vehicles...")
            vehicles = []
            statuses = ['pending', 'quality_check', 'approved', 'rejected', 'unloaded']
            for i in range(15):
                vehicle = Vehicle(
                    vehicle_number=f'HR{26 + i}A{1000 + i}',
                    supplier_id=random.randint(1, 5),
                    driver_name=f'Driver {i+1}',
                    driver_phone=f'987654{3000+i}',
                    arrival_time=datetime.now() - timedelta(days=random.randint(0, 30)),
                    entry_time=datetime.now() - timedelta(days=random.randint(0, 30)),
                    status=random.choice(statuses),
                    quality_category=random.choice(['Mill', 'Low Mill', 'HD']),
                    owner_approved=random.choice([True, False]),
                    net_weight_before=random.uniform(25000, 35000),
                    net_weight_after=random.uniform(5000, 8000),
                    godown_id=random.randint(1, 8) if random.choice([True, False]) else None
                )
                if vehicle.net_weight_before and vehicle.net_weight_after:
                    vehicle.final_weight = vehicle.net_weight_before - vehicle.net_weight_after
                vehicles.append(vehicle)
            db.session.add_all(vehicles)
            db.session.commit()

            # 8. Create Quality Tests
            print("Creating quality tests...")
            quality_tests = []
            for i, vehicle in enumerate(vehicles[:10]):
                quality_test = QualityTest(
                    vehicle_id=vehicle.id,
                    sample_bags_tested=random.randint(3, 8),
                    total_bags=random.randint(100, 300),
                    category_assigned=random.choice(['Mill', 'Low Mill', 'HD']),
                    moisture_content=random.uniform(10.5, 14.2),
                    foreign_matter=random.uniform(0.1, 2.5),
                    broken_grains=random.uniform(1.0, 4.5),
                    shrivelled_broken=random.uniform(2.0, 6.0),
                    damaged=random.uniform(0.5, 3.0),
                    weevilled=random.uniform(0.1, 1.5),
                    other_food_grains=random.uniform(0.0, 1.0),
                    sprouted=random.uniform(0.0, 0.5),
                    immature=random.uniform(0.5, 2.0),
                    test_weight=random.uniform(75.0, 82.0),
                    gluten=random.uniform(28.0, 35.0),
                    protein=random.uniform(11.0, 14.5),
                    falling_number=random.uniform(250, 400),
                    ash_content=random.uniform(0.5, 0.8),
                    wet_gluten=random.uniform(26.0, 32.0),
                    dry_gluten=random.uniform(9.0, 12.0),
                    sedimentation_value=random.uniform(25.0, 45.0),
                    test_result=random.choice(['Passed', 'Failed', 'Conditional']),
                    tested_by='Lab Technician',
                    quality_notes=f'Quality test completed for vehicle {vehicle.vehicle_number}',
                    lab_instructor=random.choice(['Dr. Sharma', 'Dr. Patel', 'Dr. Kumar']),
                    test_time=datetime.now() - timedelta(days=random.randint(0, 15)),
                    approved=random.choice([True, False])
                )
                quality_tests.append(quality_test)
            db.session.add_all(quality_tests)
            db.session.commit()

            # 9. Create Transfers
            print("Creating transfers...")
            transfers = []
            for i in range(12):
                transfer = Transfer(
                    from_godown_id=random.randint(1, 8),
                    to_precleaning_bin_id=random.randint(1, 5),
                    quantity=random.uniform(15.0, 45.0),
                    transfer_type='godown_to_precleaning',
                    operator=f'Operator {i+1}',
                    transfer_time=datetime.now() - timedelta(days=random.randint(0, 20)),
                    notes=f'Transfer {i+1} completed successfully'
                )
                transfers.append(transfer)
            db.session.add_all(transfers)
            db.session.commit()

            # 10. Create Cleaning Machines
            print("Creating cleaning machines...")
            cleaning_machines = [
                CleaningMachine(
                    name='Drum Shield Machine 1',
                    machine_type='drum_shield',
                    cleaning_frequency_hours=3,
                    location='Pre-cleaning Area A',
                    last_cleaned=datetime.now() - timedelta(hours=2)
                ),
                CleaningMachine(
                    name='Magnet Separator 1',
                    machine_type='magnet',
                    cleaning_frequency_hours=4,
                    location='Pre-cleaning Area B',
                    last_cleaned=datetime.now() - timedelta(hours=3)
                ),
                CleaningMachine(
                    name='Grain Separator 1',
                    machine_type='separator',
                    cleaning_frequency_hours=2,
                    location='Cleaning Section 1',
                    last_cleaned=datetime.now() - timedelta(hours=1)
                ),
                CleaningMachine(
                    name='Grinding Mill 1',
                    machine_type='grinding',
                    cleaning_frequency_hours=1,
                    location='Production Floor A',
                    last_cleaned=datetime.now() - timedelta(minutes=30)
                ),
                CleaningMachine(
                    name='Grinding Mill 2',
                    machine_type='grinding',
                    cleaning_frequency_hours=1,
                    location='Production Floor B',
                    last_cleaned=datetime.now() - timedelta(minutes=45)
                )
            ]
            db.session.add_all(cleaning_machines)
            db.session.commit()

            # 11. Create Cleaning Logs
            print("Creating cleaning logs...")
            cleaning_logs = []
            for i in range(8):
                cleaning_log = CleaningLog(
                    machine_id=random.randint(1, 5),
                    cleaned_by=f'Maintenance Staff {i+1}',
                    cleaning_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                    waste_collected=random.uniform(2.5, 8.5),
                    notes=f'Regular maintenance cleaning completed for machine'
                )
                cleaning_logs.append(cleaning_log)
            db.session.add_all(cleaning_logs)
            db.session.commit()

            # 12. Create Production Orders
            print("Creating production orders...")
            production_orders = []
            for i in range(10):
                order = ProductionOrder(
                    order_number=f'PO{2025}{1000+i}',
                    customer_id=random.randint(1, 5),
                    quantity=random.uniform(50.0, 200.0),
                    product=random.choice(['Maida', 'Suji', 'Chakki Atta', 'Rawa']),
                    customer=f'Customer {random.randint(1, 5)}',
                    deadline=datetime.now() + timedelta(days=random.randint(7, 30)),
                    priority=random.choice(['normal', 'high', 'urgent']),
                    description=f'Production order for {random.choice(["premium", "standard", "bulk"])} quality products',
                    status=random.choice(['pending', 'planned', 'in_progress', 'completed']),
                    created_by=f'Manager {random.randint(1, 3)}',
                    target_completion=datetime.now() + timedelta(days=random.randint(5, 25))
                )
                production_orders.append(order)
            db.session.add_all(production_orders)
            db.session.commit()

            # 13. Create Production Plans
            print("Creating production plans...")
            production_plans = []
            for order in production_orders[:7]:
                plan = ProductionPlan(
                    order_id=order.id,
                    planned_by=f'Production Planner {random.randint(1, 3)}',
                    planning_date=datetime.now() - timedelta(days=random.randint(1, 10)),
                    total_percentage=100.0,
                    status=random.choice(['draft', 'approved', 'executed'])
                )
                production_plans.append(plan)
            db.session.add_all(production_plans)
            db.session.commit()

            # 14. Create Production Plan Items
            print("Creating production plan items...")
            plan_items = []
            for plan in production_plans:
                # Create 2-3 plan items per plan
                num_items = random.randint(2, 3)
                percentages = [random.uniform(20, 50) for _ in range(num_items)]
                # Normalize to 100%
                total = sum(percentages)
                percentages = [p/total * 100 for p in percentages]
                
                for i, percentage in enumerate(percentages):
                    order = production_orders[plan.order_id - 1]
                    quantity = (percentage / 100) * order.quantity
                    item = ProductionPlanItem(
                        plan_id=plan.id,
                        precleaning_bin_id=random.randint(1, 5),
                        percentage=percentage,
                        quantity=quantity
                    )
                    plan_items.append(item)
            db.session.add_all(plan_items)
            db.session.commit()

            # 15. Create Finished Goods Storage
            print("Creating finished goods storage...")
            storage_areas = [
                FinishedGoodsStorage(name='Storage Area 1', capacity=1000.0, current_stock=650.5),
                FinishedGoodsStorage(name='Storage Area 2', capacity=1200.0, current_stock=890.2),
                FinishedGoodsStorage(name='Storage Area 3', capacity=800.0, current_stock=345.8),
                FinishedGoodsStorage(name='Bag Storage', capacity=2000.0, current_stock=1450.7),
                FinishedGoodsStorage(name='Bulk Storage', capacity=1500.0, current_stock=980.3)
            ]
            db.session.add_all(storage_areas)
            db.session.commit()

            # 16. Create Storage Areas (for production)
            print("Creating production storage areas...")
            prod_storage_areas = [
                StorageArea(name='Production Storage 1', capacity_kg=50000, current_stock_kg=32500, location='Floor A'),
                StorageArea(name='Production Storage 2', capacity_kg=60000, current_stock_kg=45200, location='Floor B'),
                StorageArea(name='Packing Area 1', capacity_kg=30000, current_stock_kg=18500, location='Packing Floor'),
                StorageArea(name='Quality Hold Area', capacity_kg=20000, current_stock_kg=8900, location='QC Section')
            ]
            db.session.add_all(prod_storage_areas)
            db.session.commit()

            # 17. Create Finished Goods
            print("Creating finished goods...")
            finished_goods = []
            for i in range(8):
                finished_good = FinishedGoods(
                    order_id=random.randint(1, len(production_orders)),
                    product_id=random.randint(1, 5),
                    quantity=random.uniform(25.0, 150.0),
                    storage_type=random.choice(['bags', 'shallow']),
                    bag_weight=random.choice([25.0, 30.0, 50.0]),
                    bag_count=random.randint(20, 100),
                    storage_id=random.randint(1, 5),
                    batch_number=f'BATCH{2025}{1000+i}',
                    production_date=datetime.now() - timedelta(days=random.randint(1, 15))
                )
                finished_goods.append(finished_good)
            db.session.add_all(finished_goods)
            db.session.commit()

            # 18. Create Sales Orders
            print("Creating sales orders...")
            sales_orders = []
            for i in range(12):
                order = SalesOrder(
                    order_number=f'SO{2025}{2000+i}',
                    customer_id=random.randint(1, 5),
                    salesman=f'Sales Executive {random.randint(1, 4)}',
                    order_date=datetime.now() - timedelta(days=random.randint(0, 20)),
                    delivery_date=datetime.now() + timedelta(days=random.randint(3, 15)),
                    total_quantity=random.uniform(100.0, 500.0),
                    delivered_quantity=random.uniform(0.0, 200.0),
                    status=random.choice(['pending', 'partial', 'completed'])
                )
                order.pending_quantity = order.total_quantity - order.delivered_quantity
                sales_orders.append(order)
            db.session.add_all(sales_orders)
            db.session.commit()

            # 19. Create Sales Order Items
            print("Creating sales order items...")
            sales_order_items = []
            for order in sales_orders:
                # Create 1-3 items per order
                num_items = random.randint(1, 3)
                for i in range(num_items):
                    item = SalesOrderItem(
                        sales_order_id=order.id,
                        product_id=random.randint(1, 5),
                        quantity=random.uniform(20.0, 150.0),
                        delivered_quantity=random.uniform(0.0, 100.0)
                    )
                    item.pending_quantity = item.quantity - item.delivered_quantity
                    sales_order_items.append(item)
            db.session.add_all(sales_order_items)
            db.session.commit()

            # 20. Create Dispatch Vehicles
            print("Creating dispatch vehicles...")
            dispatch_vehicles = [
                DispatchVehicle(
                    vehicle_number='DL1CA1234',
                    driver_name='Rakesh Kumar',
                    driver_phone='9876543301',
                    state='Delhi',
                    city='New Delhi',
                    capacity=25.0,
                    status='available'
                ),
                DispatchVehicle(
                    vehicle_number='MH2AB5678',
                    driver_name='Sunil Patil',
                    driver_phone='9876543302',
                    state='Maharashtra',
                    city='Mumbai',
                    capacity=30.0,
                    status='dispatched'
                ),
                DispatchVehicle(
                    vehicle_number='KA3BC9012',
                    driver_name='Ravi Reddy',
                    driver_phone='9876543303',
                    state='Karnataka',
                    city='Bangalore',
                    capacity=35.0,
                    status='available'
                ),
                DispatchVehicle(
                    vehicle_number='TN4CD3456',
                    driver_name='Murugan S',
                    driver_phone='9876543304',
                    state='Tamil Nadu',
                    city='Chennai',
                    capacity=28.0,
                    status='blocked'
                ),
                DispatchVehicle(
                    vehicle_number='WB5DE7890',
                    driver_name='Bijoy Das',
                    driver_phone='9876543305',
                    state='West Bengal',
                    city='Kolkata',
                    capacity=32.0,
                    status='available'
                )
            ]
            db.session.add_all(dispatch_vehicles)
            db.session.commit()

            # 21. Create Dispatches
            print("Creating dispatches...")
            dispatches = []
            for i in range(10):
                dispatch = Dispatch(
                    dispatch_number=f'DISP{2025}{3000+i}',
                    sales_order_id=random.randint(1, len(sales_orders)),
                    vehicle_id=random.randint(1, 5),
                    dispatch_date=datetime.now() - timedelta(days=random.randint(0, 10)),
                    quantity=random.uniform(20.0, 100.0),
                    status=random.choice(['loaded', 'in_transit', 'delivered']),
                    delivered_by=f'Delivery Executive {random.randint(1, 3)}',
                    delivery_date=datetime.now() - timedelta(days=random.randint(0, 5)) if random.choice([True, False]) else None
                )
                dispatches.append(dispatch)
            db.session.add_all(dispatches)
            db.session.commit()

            # 22. Create Sales Dispatches
            print("Creating sales dispatches...")
            sales_dispatches = []
            for i in range(8):
                sales_dispatch = SalesDispatch(
                    order_id=random.randint(1, len(production_orders)),
                    customer_id=random.randint(1, 5),
                    product_id=random.randint(1, 5),
                    quantity=random.uniform(25.0, 80.0),
                    dispatch_date=datetime.now() - timedelta(days=random.randint(0, 12)),
                    vehicle_number=f'TN{random.randint(10,99)}AB{random.randint(1000,9999)}',
                    driver_name=f'Driver {random.randint(10,20)}',
                    notes=f'Dispatch completed successfully - Order {i+1}',
                    created_by=f'Dispatch Manager {random.randint(1, 2)}'
                )
                sales_dispatches.append(sales_dispatch)
            db.session.add_all(sales_dispatches)
            db.session.commit()

            # 23. Create Dispatch Items
            print("Creating dispatch items...")
            dispatch_items = []
            for dispatch in dispatches:
                # Create 1-2 items per dispatch
                num_items = random.randint(1, 2)
                for i in range(num_items):
                    item = DispatchItem(
                        dispatch_id=dispatch.id,
                        product_id=random.randint(1, 5),
                        quantity=random.uniform(10.0, 50.0),
                        bag_count=random.randint(10, 50)
                    )
                    dispatch_items.append(item)
            db.session.add_all(dispatch_items)
            db.session.commit()

            # 24. Create Users
            print("Creating users...")
            users = [
                User(username='admin', role='admin', phone='9876543400'),
                User(username='production_manager', role='production_manager', phone='9876543401'),
                User(username='operator1', role='operator', phone='9876543402'),
                User(username='operator2', role='operator', phone='9876543403'),
                User(username='lab_instructor1', role='lab_instructor', phone='9876543404'),
                User(username='lab_instructor2', role='lab_instructor', phone='9876543405'),
                User(username='quality_manager', role='admin', phone='9876543406'),
                User(username='dispatch_manager', role='production_manager', phone='9876543407')
            ]
            db.session.add_all(users)
            db.session.commit()

            # 25. Create Cleaning Bins
            print("Creating cleaning bins...")
            cleaning_bins = [
                CleaningBin(
                    name='24-Hour Cleaning Bin 1',
                    capacity=60.0,
                    current_stock=45.2,
                    status='occupied',
                    location='Cleaning Area A',
                    cleaning_type='24_hour'
                ),
                CleaningBin(
                    name='24-Hour Cleaning Bin 2',
                    capacity=65.0,
                    current_stock=0.0,
                    status='empty',
                    location='Cleaning Area A',
                    cleaning_type='24_hour'
                ),
                CleaningBin(
                    name='12-Hour Cleaning Bin 1',
                    capacity=50.0,
                    current_stock=32.8,
                    status='cleaning',
                    location='Cleaning Area B',
                    cleaning_type='12_hour'
                ),
                CleaningBin(
                    name='12-Hour Cleaning Bin 2',
                    capacity=55.0,
                    current_stock=0.0,
                    status='empty',
                    location='Cleaning Area B',
                    cleaning_type='12_hour'
                )
            ]
            db.session.add_all(cleaning_bins)
            db.session.commit()

            # 26. Create Production Jobs
            print("Creating production jobs...")
            production_jobs = []
            for i in range(6):
                job = ProductionJobNew(
                    job_number=f'JOB{datetime.now().strftime("%Y%m%d")}{1000+i}',
                    order_id=random.randint(1, min(7, len(production_orders))),
                    plan_id=random.randint(1, len(production_plans)),
                    stage=random.choice(['transfer', 'cleaning', 'grinding', 'packing']),
                    status=random.choice(['pending', 'in_progress', 'completed', 'paused']),
                    started_at=datetime.now() - timedelta(hours=random.randint(1, 48)) if random.choice([True, False]) else None,
                    completed_at=datetime.now() - timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None,
                    started_by=f'Operator {random.randint(1, 5)}',
                    completed_by=f'Operator {random.randint(1, 5)}' if random.choice([True, False]) else None,
                    notes=f'Production job {i+1} for order processing'
                )
                production_jobs.append(job)
            db.session.add_all(production_jobs)
            db.session.commit()

            # 27. Create Production Transfers
            print("Creating production transfers...")
            production_transfers = []
            for job in production_jobs[:3]:
                transfer = ProductionTransfer(
                    job_id=job.id,
                    from_precleaning_bin_id=random.randint(1, 5),
                    quantity_transferred=random.uniform(20.0, 60.0),
                    transfer_time=datetime.now() - timedelta(hours=random.randint(1, 72)),
                    operator_name=f'Transfer Operator {random.randint(1, 3)}'
                )
                production_transfers.append(transfer)
            db.session.add_all(production_transfers)
            db.session.commit()

            # 28. Create Cleaning Processes
            print("Creating cleaning processes...")
            cleaning_processes = []
            for i, job in enumerate(production_jobs[:4]):
                process_type = random.choice(['24_hour', '12_hour'])
                duration = 24 if process_type == '24_hour' else 12
                start_time = datetime.now() - timedelta(hours=random.randint(1, duration+5))
                
                process = CleaningProcess(
                    job_id=job.id,
                    process_type=process_type,
                    cleaning_bin_id=random.randint(1, 4),
                    duration_hours=duration,
                    target_moisture=random.uniform(11.0, 13.5) if process_type == '12_hour' else None,
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=duration),
                    actual_end_time=start_time + timedelta(hours=duration, minutes=random.randint(-30, 60)) if random.choice([True, False]) else None,
                    start_moisture=random.uniform(13.5, 16.0),
                    end_moisture=random.uniform(11.0, 13.0),
                    water_added_liters=random.uniform(50.0, 200.0) if process_type == '12_hour' else 0.0,
                    waste_collected_kg=random.uniform(5.0, 25.0),
                    machine_name=f'Cleaning Machine {random.randint(1, 3)}',
                    status=random.choice(['pending', 'running', 'completed']),
                    operator_name=f'Cleaning Operator {random.randint(1, 4)}',
                    completed_by=f'Supervisor {random.randint(1, 2)}' if random.choice([True, False]) else None,
                    notes=f'Cleaning process {i+1} - {process_type} treatment'
                )
                cleaning_processes.append(process)
            db.session.add_all(cleaning_processes)
            db.session.commit()

            # 29. Create Grinding Processes
            print("Creating grinding processes...")
            grinding_processes = []
            for i, job in enumerate(production_jobs[:3]):
                input_qty = random.uniform(800.0, 1500.0)
                main_products = input_qty * random.uniform(0.75, 0.77)
                bran_qty = input_qty * random.uniform(0.23, 0.25)
                total_output = main_products + bran_qty
                
                process = GrindingProcess(
                    job_id=job.id,
                    machine_name=f'Grinding Mill {random.randint(1, 3)}',
                    start_time=datetime.now() - timedelta(hours=random.randint(2, 24)),
                    end_time=datetime.now() - timedelta(hours=random.randint(1, 12)) if random.choice([True, False]) else None,
                    input_quantity_kg=input_qty,
                    total_output_kg=total_output,
                    main_products_kg=main_products,
                    bran_kg=bran_qty,
                    bran_percentage=(bran_qty/input_qty)*100,
                    status=random.choice(['pending', 'in_progress', 'completed']),
                    operator_name=f'Grinding Operator {random.randint(1, 3)}',
                    notes=f'Grinding process {i+1} completed successfully'
                )
                grinding_processes.append(process)
            db.session.add_all(grinding_processes)
            db.session.commit()

            # 30. Create Product Outputs
            print("Creating product outputs...")
            product_outputs = []
            for process in grinding_processes:
                # Main product output
                main_output = ProductOutput(
                    grinding_process_id=process.id,
                    product_id=random.randint(1, 5),  # Main products
                    quantity_produced_kg=process.main_products_kg,
                    percentage=(process.main_products_kg/process.input_quantity_kg)*100
                )
                product_outputs.append(main_output)
                
                # Bran output
                bran_output = ProductOutput(
                    grinding_process_id=process.id,
                    product_id=6,  # Wheat Bran
                    quantity_produced_kg=process.bran_kg,
                    percentage=(process.bran_kg/process.input_quantity_kg)*100
                )
                product_outputs.append(bran_output)
            db.session.add_all(product_outputs)
            db.session.commit()

            # 31. Create Packing Processes
            print("Creating packing processes...")
            packing_processes = []
            for i, job in enumerate(production_jobs[:4]):
                bag_weight = random.choice([25.0, 30.0, 50.0])
                num_bags = random.randint(20, 80)
                total_packed = bag_weight * num_bags
                
                process = PackingProcess(
                    job_id=job.id,
                    product_id=random.randint(1, 5),
                    bag_weight_kg=bag_weight,
                    number_of_bags=num_bags,
                    total_packed_kg=total_packed,
                    packed_time=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    operator_name=f'Packing Operator {random.randint(1, 4)}',
                    storage_area_id=random.randint(1, 4),
                    stored_in_shallow_kg=random.uniform(50.0, 200.0)
                )
                packing_processes.append(process)
            db.session.add_all(packing_processes)
            db.session.commit()

            # 32. Create Storage Transfers
            print("Creating storage transfers...")
            storage_transfers = []
            for i in range(6):
                transfer = StorageTransfer(
                    from_storage_id=random.randint(1, 4),
                    to_storage_id=random.randint(1, 4),
                    product_id=random.randint(1, 5),
                    quantity_kg=random.uniform(100.0, 500.0),
                    transfer_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                    operator_name=f'Storage Operator {random.randint(1, 3)}',
                    reason=random.choice(['Space optimization', 'Quality segregation', 'Order fulfillment', 'Maintenance'])
                )
                storage_transfers.append(transfer)
            db.session.add_all(storage_transfers)
            db.session.commit()

            # 33. Create Process Reminders
            print("Creating process reminders...")
            process_reminders = []
            for job in production_jobs[:3]:
                reminder = ProcessReminder(
                    job_id=job.id,
                    process_type=random.choice(['cleaning_24h', 'cleaning_12h', 'machine_cleaning']),
                    reminder_time=datetime.now() + timedelta(minutes=random.randint(5, 120)),
                    reminder_type=random.choice(['5min', '10min', '30min']),
                    status=random.choice(['pending', 'sent', 'dismissed']),
                    message=f'Process reminder for job {job.job_number}'
                )
                process_reminders.append(reminder)
            db.session.add_all(process_reminders)
            db.session.commit()

            # 34. Create Cleaning Reminders
            print("Creating cleaning reminders...")
            cleaning_reminders = []
            for machine in cleaning_machines:
                reminder = CleaningReminder(
                    machine_id=machine.id,
                    due_time=datetime.now() + timedelta(hours=random.randint(1, 6)),
                    reminder_sent=random.choice([True, False]),
                    user_notified=f'Operator {random.randint(1, 5)}',
                    created_at=datetime.now() - timedelta(hours=random.randint(1, 24))
                )
                cleaning_reminders.append(reminder)
            db.session.add_all(cleaning_reminders)
            db.session.commit()

            print("✅ Dummy data population completed successfully!")
            print(f"Created records in all {34} table categories with proper relationships.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating dummy data: {e}")
            raise e

if __name__ == '__main__':
    populate_dummy_data()
