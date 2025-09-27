
#!/usr/bin/env python3
"""
Comprehensive data population script for the wheat processing application.
This script adds sample data to all tables including the specific godowns from the image.
"""

import os
from datetime import datetime, timedelta
import random
from app import app, db
from models import *

def populate_all_tables():
    """Populate all tables with comprehensive sample data"""
    with app.app_context():
        try:
            print("🌾 Starting comprehensive data population for wheat processing system...")
            
            # Clear existing data first
            print("🗑️ Clearing existing data...")
            db.session.query(ProcessReminder).delete()
            db.session.query(StorageTransfer).delete()
            db.session.query(ProductOutput).delete()
            db.session.query(PackingProcess).delete()
            db.session.query(GrindingProcess).delete()
            db.session.query(CleaningProcess).delete()
            db.session.query(ManualCleaningLog).delete()
            db.session.query(CleaningReminder).delete()
            db.session.query(FinishedGoods).delete()
            db.session.query(ProductionPlanItem).delete()
            db.session.query(ProductionPlan).delete()
            db.session.query(ProductionOrder).delete()
            db.session.query(Transfer).delete()
            db.session.query(QualityTest).delete()
            db.session.query(Vehicle).delete()
            db.session.commit()

            # 1. Create Suppliers
            print("📦 Creating suppliers...")
            if not Supplier.query.first():
                suppliers = [
                    Supplier(company_name='Rajasthan Wheat Co.', contact_person='Rajesh Kumar', phone='9876543210', 
                           city='Jaipur', address='123 Grain Market, Jaipur', state='Rajasthan', postal_code='302001'),
                    Supplier(company_name='Punjab Agro Traders', contact_person='Harpreet Singh', phone='9876543211', 
                           city='Ludhiana', address='456 Mandi Road, Ludhiana', state='Punjab', postal_code='141001'),
                    Supplier(company_name='MP Wheat Suppliers', contact_person='Ravi Sharma', phone='9876543212', 
                           city='Indore', address='789 Krishi Upaj Mandi, Indore', state='Madhya Pradesh', postal_code='452001'),
                    Supplier(company_name='UP Premium Grains', contact_person='Suresh Gupta', phone='9876543213', 
                           city='Kanpur', address='321 Grain Exchange, Kanpur', state='Uttar Pradesh', postal_code='208001'),
                    Supplier(company_name='Haryana Wheat Mills', contact_person='Vikram Singh', phone='9876543214', 
                           city='Karnal', address='654 Agricultural Market, Karnal', state='Haryana', postal_code='132001')
                ]
                db.session.add_all(suppliers)
                db.session.commit()
                print("✓ Suppliers created")

            # 2. Create Customers
            print("🏢 Creating customers...")
            if not Customer.query.first():
                customers = [
                    Customer(company_name='Delhi Bakery Chain', contact_person='Mohan Lal', phone='9876543220', 
                           city='Delhi', address='100 Connaught Place, Delhi', state='Delhi', postal_code='110001'),
                    Customer(company_name='Mumbai Food Industries', contact_person='Anil Patel', phone='9876543221', 
                           city='Mumbai', address='200 Industrial Estate, Mumbai', state='Maharashtra', postal_code='400001'),
                    Customer(company_name='Bangalore Flour Mills', contact_person='Sunil Kumar', phone='9876543222', 
                           city='Bangalore', address='300 Electronic City, Bangalore', state='Karnataka', postal_code='560001'),
                    Customer(company_name='Chennai Food Products', contact_person='Raman Iyer', phone='9876543223', 
                           city='Chennai', address='400 Anna Nagar, Chennai', state='Tamil Nadu', postal_code='600001'),
                    Customer(company_name='Hyderabad Grain Co.', contact_person='Krishna Reddy', phone='9876543224', 
                           city='Hyderabad', address='500 HITEC City, Hyderabad', state='Telangana', postal_code='500001')
                ]
                db.session.add_all(customers)
                db.session.commit()
                print("✓ Customers created")

            # 3. Create Products
            print("📦 Creating products...")
            if not Product.query.first():
                products = [
                    Product(name='Premium Maida', category='Main Product', description='High-quality refined wheat flour for premium bakery'),
                    Product(name='Standard Maida', category='Main Product', description='Standard refined wheat flour for general use'),
                    Product(name='Suji (Semolina)', category='Main Product', description='Coarse wheat semolina for traditional recipes'),
                    Product(name='Fine Suji', category='Main Product', description='Fine-grade semolina for delicate preparations'),
                    Product(name='Chakki Atta', category='Main Product', description='Stone-ground whole wheat flour'),
                    Product(name='Multigrain Atta', category='Main Product', description='Mixed grain flour with wheat base'),
                    Product(name='Wheat Bran', category='By-product', description='Nutritious wheat bran for animal feed'),
                    Product(name='Wheat Germ', category='By-product', description='Vitamin-rich wheat germ extract'),
                    Product(name='Broken Wheat', category='By-product', description='Cracked wheat for traditional dishes'),
                    Product(name='Flour Dust', category='By-product', description='Fine dust collected during processing')
                ]
                db.session.add_all(products)
                db.session.commit()
                print("✓ Products created")

            # 4. Create Godown Types (matching the image)
            print("🏭 Creating godown types...")
            if not GodownType.query.first():
                godown_types = [
                    GodownType(name='Mill', description='Mill quality wheat storage'),
                    GodownType(name='Low Mill', description='Lower grade mill wheat storage'),
                    GodownType(name='HD', description='High density wheat storage')
                ]
                db.session.add_all(godown_types)
                db.session.commit()
                print("✓ Godown types created")

            # 5. Create Godowns (exactly matching the image)
            print("🏗️ Creating godowns to match the image...")
            # Clear existing godowns
            Godown.query.delete()
            db.session.commit()
            
            godowns = [
                Godown(name='Godown A', type_id=1, capacity=100.0, current_stock=0.0),  # Mill type, 100 kg capacity
                Godown(name='Godown B', type_id=2, capacity=150.0, current_stock=0.0),  # Low Mill type, 150 kg capacity  
                Godown(name='Godown C', type_id=3, capacity=200.0, current_stock=0.0)   # HD type, 200 kg capacity
            ]
            db.session.add_all(godowns)
            db.session.commit()
            print("✓ Godowns created to match image specifications")

            # 6. Create Pre-cleaning Bins
            print("🔄 Creating pre-cleaning bins...")
            if not PrecleaningBin.query.first():
                precleaning_bins = [
                    PrecleaningBin(name='Pre-cleaning Bin A1', capacity=80.0, current_stock=65.5),
                    PrecleaningBin(name='Pre-cleaning Bin A2', capacity=85.0, current_stock=70.3),
                    PrecleaningBin(name='Pre-cleaning Bin B1', capacity=75.0, current_stock=45.7),
                    PrecleaningBin(name='Pre-cleaning Bin B2', capacity=90.0, current_stock=80.2),
                    PrecleaningBin(name='Pre-cleaning Bin C1', capacity=70.0, current_stock=55.8),
                    PrecleaningBin(name='Pre-cleaning Bin C2', capacity=85.0, current_stock=65.4),
                    PrecleaningBin(name='Pre-cleaning Bin D1', capacity=60.0, current_stock=45.5),
                    PrecleaningBin(name='Pre-cleaning Bin D2', capacity=80.0, current_stock=70.7)
                ]
                db.session.add_all(precleaning_bins)
                db.session.commit()
                print("✓ Pre-cleaning bins created")

            # 7. Create Cleaning Bins
            print("🧹 Creating cleaning bins...")
            if not CleaningBin.query.first():
                cleaning_bins = [
                    CleaningBin(name='24-Hour Cleaning Bin #1', capacity=100.0, current_stock=0.0, status='available', 
                              location='24-Hour Cleaning Area A', cleaning_type='24_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #2', capacity=110.0, current_stock=85.5, status='cleaning', 
                              location='24-Hour Cleaning Area B', cleaning_type='24_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #3', capacity=105.0, current_stock=0.0, status='available', 
                              location='24-Hour Cleaning Area C', cleaning_type='24_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #1', capacity=75.0, current_stock=0.0, status='available', 
                              location='12-Hour Cleaning Area A', cleaning_type='12_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #2', capacity=80.0, current_stock=65.3, status='cleaning', 
                              location='12-Hour Cleaning Area B', cleaning_type='12_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #3', capacity=70.0, current_stock=0.0, status='available', 
                              location='12-Hour Cleaning Area C', cleaning_type='12_hour')
                ]
                db.session.add_all(cleaning_bins)
                db.session.commit()
                print("✓ Cleaning bins created")

            # 8. Create Storage Areas
            print("📦 Creating storage areas...")
            if not StorageArea.query.first():
                storage_areas = [
                    StorageArea(name='Storage Area A', capacity_kg=5000.0, current_stock_kg=3500.0, 
                              location='Main Warehouse Section A'),
                    StorageArea(name='Storage Area B', capacity_kg=4500.0, current_stock_kg=2800.0, 
                              location='Main Warehouse Section B'),
                    StorageArea(name='Storage Area C', capacity_kg=4000.0, current_stock_kg=2200.0, 
                              location='Secondary Warehouse Section A'),
                    StorageArea(name='Storage Area D', capacity_kg=5500.0, current_stock_kg=4100.0, 
                              location='Secondary Warehouse Section B'),
                    StorageArea(name='Premium Storage', capacity_kg=3000.0, current_stock_kg=1500.0, 
                              location='Premium Products Section'),
                    StorageArea(name='By-products Storage', capacity_kg=2500.0, current_stock_kg=1800.0, 
                              location='By-products Section')
                ]
                db.session.add_all(storage_areas)
                db.session.commit()
                print("✓ Storage areas created")

            # 9. Create Vehicles with comprehensive data
            print("🚛 Creating vehicles...")
            vehicles = []
            statuses = ['pending', 'quality_check', 'approved', 'rejected', 'unloaded']
            for i in range(20):
                vehicle = Vehicle(
                    vehicle_number=f'RJ{14+i}AB{1000+i}',
                    supplier_id=random.randint(1, 5),
                    driver_name=f'Driver {i+1}',
                    driver_phone=f'987654{3000+i}',
                    arrival_time=datetime.now() - timedelta(days=random.randint(0, 30)),
                    entry_time=datetime.now() - timedelta(days=random.randint(0, 30)),
                    status=random.choice(statuses),
                    quality_category=random.choice(['Mill', 'Low Mill', 'HD']),
                    owner_approved=random.choice([True, False]) if random.choice([True, False]) else None,
                    net_weight_before=random.uniform(25000, 35000),
                    net_weight_after=random.uniform(5000, 8000),
                    godown_id=random.randint(1, 3) if random.choice([True, False]) else None
                )
                if vehicle.net_weight_before and vehicle.net_weight_after:
                    vehicle.final_weight = vehicle.net_weight_before - vehicle.net_weight_after
                vehicles.append(vehicle)
            db.session.add_all(vehicles)
            db.session.commit()
            print("✓ Vehicles created")

            # 10. Create Quality Tests
            print("🔬 Creating quality tests...")
            quality_tests = []
            for i, vehicle in enumerate(vehicles[:15]):
                quality_test = QualityTest(
                    vehicle_id=vehicle.id,
                    sample_bags_tested=random.randint(3, 8),
                    total_bags=random.randint(100, 300),
                    category_assigned=random.choice(['Mill', 'Low Mill', 'HD']),
                    moisture_content=random.uniform(10.5, 14.2),
                    foreign_matter=random.uniform(0.1, 2.5),
                    test_weight=random.uniform(75.0, 82.0),
                    gluten=random.uniform(28.0, 35.0),
                    protein=random.uniform(11.0, 14.5),
                    falling_number=random.uniform(250, 400),
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
            print("✓ Quality tests created")

            # 11. Create Production Orders
            print("🏭 Creating production orders...")
            production_orders = []
            for i in range(12):
                order = ProductionOrder(
                    order_number=f'PRO-2025-{1000+i}',
                    customer_id=random.randint(1, 5),
                    product_id=random.randint(1, 6),
                    quantity=random.uniform(100.0, 500.0),
                    finished_good_type=random.choice(['Premium Maida', 'Standard Maida', 'Suji', 'Chakki Atta']),
                    status=random.choice(['pending', 'planning', 'cleaning', '24h_completed', 'completed']),
                    priority=random.choice(['normal', 'high', 'urgent']),
                    created_by=f'Production Manager {random.randint(1, 3)}',
                    target_completion=datetime.now() + timedelta(days=random.randint(7, 30)),
                    deadline=datetime.now() + timedelta(days=random.randint(14, 45))
                )
                production_orders.append(order)
            db.session.add_all(production_orders)
            db.session.commit()
            print("✓ Production orders created")

            # 12. Create Production Plans and Plan Items
            print("📋 Creating production plans...")
            for i, order in enumerate(production_orders[:8]):
                plan = ProductionPlan(
                    order_id=order.id,
                    planned_by=f'Production Planner {random.randint(1, 3)}',
                    total_percentage=100.0
                )
                db.session.add(plan)
                db.session.flush()
                
                # Create plan items for this plan
                bin_count = random.randint(2, 4)
                percentages = [random.uniform(15, 50) for _ in range(bin_count)]
                total = sum(percentages)
                percentages = [p/total * 100 for p in percentages]
                
                for j, percentage in enumerate(percentages):
                    plan_item = ProductionPlanItem(
                        plan_id=plan.id,
                        precleaning_bin_id=random.randint(1, 8),
                        percentage=percentage,
                        calculated_tons=(percentage / 100) * order.quantity,
                        quantity=(percentage / 100) * order.quantity
                    )
                    db.session.add(plan_item)
            
            db.session.commit()
            print("✓ Production plans and items created")

            # 13. Create Cleaning Processes
            print("🧽 Creating cleaning processes...")
            cleaning_processes = []
            for i, order in enumerate(production_orders[:6]):
                process_type = random.choice(['24_hour', '12_hour'])
                duration = 24 if process_type == '24_hour' else 12
                start_time = datetime.now() - timedelta(hours=random.randint(1, duration+5))
                
                process = CleaningProcess(
                    order_id=order.id,
                    cleaning_bin_id=random.randint(1, 6),
                    process_type=process_type,
                    duration_hours=duration,
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=duration),
                    start_moisture=random.uniform(13.5, 16.0),
                    end_moisture=random.uniform(11.0, 13.0),
                    target_moisture=random.uniform(11.0, 13.5) if process_type == '12_hour' else None,
                    water_added_liters=random.uniform(50.0, 200.0) if process_type == '12_hour' else 0.0,
                    waste_collected_kg=random.uniform(5.0, 25.0),
                    machine_name=f'Cleaning Machine {random.randint(1, 3)}',
                    operator_name=f'Cleaning Operator {random.randint(1, 4)}',
                    status=random.choice(['running', 'completed'])
                )
                cleaning_processes.append(process)
            db.session.add_all(cleaning_processes)
            db.session.commit()
            print("✓ Cleaning processes created")

            # 14. Create Manual Cleaning Logs
            print("🧼 Creating manual cleaning logs...")
            manual_cleanings = []
            for process in cleaning_processes:
                log_count = random.randint(5, 20)
                for j in range(log_count):
                    log = ManualCleaningLog(
                        order_id=process.order_id,
                        cleaning_process_id=process.id,
                        machine_name='Manual Cleaning Equipment',
                        operator_name=f'Operator {random.randint(1, 5)}',
                        cleaning_start_time=process.start_time + timedelta(minutes=j*30),
                        cleaning_end_time=process.start_time + timedelta(minutes=j*30+5),
                        duration_minutes=5.0,
                        notes=f'Manual cleaning #{j+1} for process',
                        status='completed'
                    )
                    manual_cleanings.append(log)
            db.session.add_all(manual_cleanings)
            db.session.commit()
            print("✓ Manual cleaning logs created")

            # 15. Create Grinding Sessions and Outputs
            print("⚙️ Creating grinding sessions...")
            grinding_sessions = []
            for order in production_orders[:4]:
                session = GrindingSession(
                    order_id=order.id,
                    start_time=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    b1_scale_operator=f'Scale Operator {random.randint(1, 3)}',
                    b1_scale_weight_kg=random.uniform(800.0, 1500.0),
                    grinding_machine_name=f'Grinding Mill {random.randint(1, 3)}',
                    grinding_operator=f'Grinding Operator {random.randint(1, 3)}',
                    total_input_kg=random.uniform(800.0, 1500.0),
                    status='completed'
                )
                session.total_output_kg = session.total_input_kg * 0.98  # 2% loss
                session.main_products_kg = session.total_output_kg * 0.76  # 76% main products
                session.bran_kg = session.total_output_kg * 0.24  # 24% bran
                session.main_products_percentage = 76.0
                session.bran_percentage = 24.0
                grinding_sessions.append(session)
            db.session.add_all(grinding_sessions)
            db.session.commit()
            print("✓ Grinding sessions created")

            # 16. Create Packaging Records
            print("📦 Creating packaging records...")
            packaging_records = []
            for session in grinding_sessions:
                record = PackagingRecord(
                    production_order_id=session.order_id,
                    product_name=random.choice(['Premium Maida', 'Standard Maida', 'Suji']),
                    bag_weight_kg=random.choice([25.0, 30.0, 50.0]),
                    bag_count=random.randint(15, 40),
                    total_weight_kg=0,  # Will be calculated
                    operator_name=f'Packing Operator {random.randint(1, 4)}',
                    storage_area_id=random.randint(1, 6)
                )
                record.total_weight_kg = record.bag_weight_kg * record.bag_count
                packaging_records.append(record)
            db.session.add_all(packaging_records)
            db.session.commit()
            print("✓ Packaging records created")

            # 17. Create Sales Orders and Items
            print("💼 Creating sales orders...")
            sales_orders = []
            for i in range(10):
                order = SalesOrder(
                    order_number=f'SO-2025-{2000+i}',
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

            # Create sales order items
            for order in sales_orders:
                item_count = random.randint(1, 3)
                for i in range(item_count):
                    item = SalesOrderItem(
                        sales_order_id=order.id,
                        product_id=random.randint(1, 6),
                        quantity=random.uniform(20.0, 150.0),
                        delivered_quantity=random.uniform(0.0, 100.0)
                    )
                    item.pending_quantity = item.quantity - item.delivered_quantity
                    db.session.add(item)
            db.session.commit()
            print("✓ Sales orders and items created")

            # 18. Create Dispatch Vehicles and Dispatches
            print("🚛 Creating dispatch system...")
            dispatch_vehicles = [
                DispatchVehicle(vehicle_number='DL1CA1234', driver_name='Rakesh Kumar', driver_phone='9876543301',
                               state='Delhi', city='New Delhi', capacity=25.0, status='available'),
                DispatchVehicle(vehicle_number='MH2AB5678', driver_name='Sunil Patil', driver_phone='9876543302',
                               state='Maharashtra', city='Mumbai', capacity=30.0, status='dispatched'),
                DispatchVehicle(vehicle_number='KA3BC9012', driver_name='Ravi Reddy', driver_phone='9876543303',
                               state='Karnataka', city='Bangalore', capacity=35.0, status='available'),
                DispatchVehicle(vehicle_number='TN4CD3456', driver_name='Murugan S', driver_phone='9876543304',
                               state='Tamil Nadu', city='Chennai', capacity=28.0, status='blocked')
            ]
            db.session.add_all(dispatch_vehicles)
            db.session.commit()

            # Create dispatches
            dispatches = []
            for i, sales_order in enumerate(sales_orders[:6]):
                dispatch = Dispatch(
                    dispatch_number=f'DISP-2025-{3000+i}',
                    sales_order_id=sales_order.id,
                    vehicle_id=random.randint(1, 4),
                    dispatch_date=datetime.now() - timedelta(days=random.randint(0, 10)),
                    quantity=random.uniform(20.0, 100.0),
                    status=random.choice(['loaded', 'in_transit', 'delivered']),
                    delivered_by=f'Delivery Executive {random.randint(1, 3)}'
                )
                dispatches.append(dispatch)
            db.session.add_all(dispatches)
            db.session.commit()
            print("✓ Dispatch system created")

            # 19. Create Users
            print("👥 Creating users...")
            if not User.query.first():
                users = [
                    User(username='admin', role='admin', phone='9876543250', is_blocked=False),
                    User(username='production_manager', role='production_manager', phone='9876543251', is_blocked=False),
                    User(username='lab_instructor', role='lab_instructor', phone='9876543252', is_blocked=False),
                    User(username='operator1', role='operator', phone='9876543253', is_blocked=False),
                    User(username='operator2', role='operator', phone='9876543254', is_blocked=False),
                    User(username='quality_manager', role='admin', phone='9876543255', is_blocked=False)
                ]
                db.session.add_all(users)
                db.session.commit()
                print("✓ Users created")

            # 20. Create Cleaning Machines and Logs
            print("🔧 Creating cleaning machines...")
            if not CleaningMachine.query.first():
                cleaning_machines = [
                    CleaningMachine(name='Drum Shield #1', machine_type='drum_shield', cleaning_frequency_hours=3, 
                                   location='Pre-cleaning Area A', last_cleaned=datetime.now() - timedelta(hours=2)),
                    CleaningMachine(name='Magnet Separator #1', machine_type='magnet_separator', cleaning_frequency_hours=4, 
                                   location='Pre-cleaning Area B', last_cleaned=datetime.now() - timedelta(hours=3)),
                    CleaningMachine(name='Vibro Separator #1', machine_type='vibro_separator', cleaning_frequency_hours=2, 
                                   location='Cleaning Area A', last_cleaned=datetime.now() - timedelta(hours=1))
                ]
                db.session.add_all(cleaning_machines)
                db.session.commit()

                # Create cleaning logs
                cleaning_logs = []
                for machine in cleaning_machines:
                    for i in range(3):
                        log = CleaningLog(
                            machine_id=machine.id,
                            cleaned_by=f'Maintenance Staff {i+1}',
                            cleaning_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                            waste_collected=random.uniform(2.5, 8.5),
                            notes=f'Regular maintenance cleaning completed'
                        )
                        cleaning_logs.append(log)
                db.session.add_all(cleaning_logs)
                db.session.commit()
                print("✓ Cleaning machines and logs created")

            # 21. Create Transfers
            print("↔️ Creating transfer records...")
            transfers = []
            for i in range(15):
                transfer = Transfer(
                    from_godown_id=random.randint(1, 3),
                    to_precleaning_bin_id=random.randint(1, 8),
                    quantity=random.uniform(15.0, 45.0),
                    transfer_type='godown_to_precleaning',
                    operator=f'Transfer Operator {random.randint(1, 3)}',
                    transfer_time=datetime.now() - timedelta(days=random.randint(0, 20)),
                    notes=f'Transfer {i+1} completed successfully'
                )
                transfers.append(transfer)
            db.session.add_all(transfers)
            db.session.commit()
            print("✓ Transfer records created")

            # 22. Update godown stock levels after transfers
            print("📊 Updating stock levels...")
            for godown in Godown.query.all():
                outgoing_transfers = Transfer.query.filter_by(from_godown_id=godown.id).all()
                total_transferred = sum(t.quantity for t in outgoing_transfers)
                # Add some initial stock and subtract transfers
                initial_stock = random.uniform(50.0, godown.capacity * 0.8)
                godown.current_stock = max(0, initial_stock - total_transferred)
            
            # Update precleaning bin stocks
            for bin in PrecleaningBin.query.all():
                incoming_transfers = Transfer.query.filter_by(to_precleaning_bin_id=bin.id).all()
                total_received = sum(t.quantity for t in incoming_transfers)
                bin.current_stock = min(bin.capacity, total_received)
            
            db.session.commit()
            
            print("\n🎉 COMPREHENSIVE DATA POPULATION COMPLETED! 🎉")
            print("=" * 60)
            print("📈 Summary of created records:")
            print(f"   👥 Suppliers: {Supplier.query.count()}")
            print(f"   🏢 Customers: {Customer.query.count()}")
            print(f"   📦 Products: {Product.query.count()}")
            print(f"   🏗️ Godowns: {Godown.query.count()}")
            print(f"   🔄 Pre-cleaning Bins: {PrecleaningBin.query.count()}")
            print(f"   🧹 Cleaning Bins: {CleaningBin.query.count()}")
            print(f"   📦 Storage Areas: {StorageArea.query.count()}")
            print(f"   🚛 Vehicles: {Vehicle.query.count()}")
            print(f"   🔬 Quality Tests: {QualityTest.query.count()}")
            print(f"   🏭 Production Orders: {ProductionOrder.query.count()}")
            print(f"   📋 Production Plans: {ProductionPlan.query.count()}")
            print(f"   🧽 Cleaning Processes: {CleaningProcess.query.count()}")
            print(f"   📦 Packaging Records: {PackagingRecord.query.count()}")
            print(f"   💼 Sales Orders: {SalesOrder.query.count()}")
            print(f"   🚛 Dispatch Vehicles: {DispatchVehicle.query.count()}")
            print(f"   ↔️ Transfers: {Transfer.query.count()}")
            print(f"   👥 Users: {User.query.count()}")
            
            print("\n🌾 Godown Details (matching your image):")
            for godown in Godown.query.all():
                utilization = (godown.current_stock / godown.capacity * 100) if godown.capacity > 0 else 0
                print(f"   {godown.name}: {godown.godown_type.name} type, {godown.capacity}kg capacity, {godown.current_stock:.1f}kg stock ({utilization:.1f}% full)")
            
            print("=" * 60)
            print("✅ Your wheat processing system is now fully populated with realistic data!")
            print("🏭 All godowns match the specifications from your image!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during data population: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    populate_all_tables()
