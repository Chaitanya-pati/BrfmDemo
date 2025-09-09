
#!/usr/bin/env python3
"""
Comprehensive data population script for the wheat processing application.
This script adds sample data to all tables including pre-cleaning bins with realistic quantities.
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

            # 4. Create Godown Types
            print("🏭 Creating godown types...")
            if not GodownType.query.first():
                godown_types = [
                    GodownType(name='Premium', description='Premium quality wheat storage'),
                    GodownType(name='Standard', description='Standard quality wheat storage'),
                    GodownType(name='Low Grade', description='Lower grade wheat storage'),
                    GodownType(name='Organic', description='Certified organic wheat storage'),
                    GodownType(name='Export Quality', description='Export-grade wheat storage')
                ]
                db.session.add_all(godown_types)
                db.session.commit()
                print("✓ Godown types created")

            # 5. Create Godowns
            print("🏗️ Creating godowns...")
            if not Godown.query.first():
                godowns = [
                    Godown(name='Godown A1', type_id=1, capacity=500.0, current_stock=425.5, location='North Wing Section A'),
                    Godown(name='Godown A2', type_id=1, capacity=600.0, current_stock=480.3, location='North Wing Section B'),
                    Godown(name='Godown B1', type_id=2, capacity=450.0, current_stock=380.7, location='East Wing Section A'),
                    Godown(name='Godown B2', type_id=2, capacity=550.0, current_stock=425.2, location='East Wing Section B'),
                    Godown(name='Godown C1', type_id=3, capacity=400.0, current_stock=290.8, location='South Wing Section A'),
                    Godown(name='Godown C2', type_id=3, capacity=350.0, current_stock=275.4, location='South Wing Section B'),
                    Godown(name='Godown D1', type_id=4, capacity=300.0, current_stock=180.5, location='West Wing Organic Section'),
                    Godown(name='Godown E1', type_id=5, capacity=700.0, current_stock=550.0, location='Export Quality Section')
                ]
                db.session.add_all(godowns)
                db.session.commit()
                print("✓ Godowns created")

            # 6. Create Pre-cleaning Bins with Enhanced Data
            print("🔄 Creating pre-cleaning bins...")
            if not PrecleaningBin.query.first():
                precleaning_bins = [
                    PrecleaningBin(name='Pre-cleaning Bin A1', capacity=150.0, current_stock=125.5),
                    PrecleaningBin(name='Pre-cleaning Bin A2', capacity=200.0, current_stock=185.3),
                    PrecleaningBin(name='Pre-cleaning Bin B1', capacity=175.0, current_stock=95.7),
                    PrecleaningBin(name='Pre-cleaning Bin B2', capacity=180.0, current_stock=165.2),
                    PrecleaningBin(name='Pre-cleaning Bin C1', capacity=220.0, current_stock=205.8),
                    PrecleaningBin(name='Pre-cleaning Bin C2', capacity=190.0, current_stock=75.4),
                    PrecleaningBin(name='Pre-cleaning Bin D1', capacity=160.0, current_stock=140.5),
                    PrecleaningBin(name='Pre-cleaning Bin D2', capacity=170.0, current_stock=155.7),
                    PrecleaningBin(name='Pre-cleaning Bin E1', capacity=140.0, current_stock=125.3),
                    PrecleaningBin(name='Pre-cleaning Bin E2', capacity=165.0, current_stock=145.8)
                ]
                db.session.add_all(precleaning_bins)
                db.session.commit()
                print("✓ Pre-cleaning bins created")

            # 7. Create Cleaning Bins
            print("🧹 Creating cleaning bins...")
            if not CleaningBin.query.first():
                cleaning_bins = [
                    CleaningBin(name='24-Hour Cleaning Bin #1', capacity=200.0, current_stock=0.0, status='available', 
                              location='24-Hour Cleaning Area A', cleaning_type='24_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #2', capacity=220.0, current_stock=180.5, status='cleaning', 
                              location='24-Hour Cleaning Area B', cleaning_type='24_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #3', capacity=210.0, current_stock=0.0, status='available', 
                              location='24-Hour Cleaning Area C', cleaning_type='24_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #1', capacity=150.0, current_stock=0.0, status='available', 
                              location='12-Hour Cleaning Area A', cleaning_type='12_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #2', capacity=160.0, current_stock=125.3, status='cleaning', 
                              location='12-Hour Cleaning Area B', cleaning_type='12_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #3', capacity=155.0, current_stock=0.0, status='available', 
                              location='12-Hour Cleaning Area C', cleaning_type='12_hour')
                ]
                db.session.add_all(cleaning_bins)
                db.session.commit()
                print("✓ Cleaning bins created")

            # 8. Create Storage Areas
            print("📦 Creating storage areas...")
            if not StorageArea.query.first():
                storage_areas = [
                    StorageArea(name='Storage Area A', capacity_kg=8000.0, current_stock_kg=6500.0, 
                              location='Main Warehouse Section A'),
                    StorageArea(name='Storage Area B', capacity_kg=7500.0, current_stock_kg=5800.0, 
                              location='Main Warehouse Section B'),
                    StorageArea(name='Storage Area C', capacity_kg=6000.0, current_stock_kg=4200.0, 
                              location='Secondary Warehouse Section A'),
                    StorageArea(name='Storage Area D', capacity_kg=6500.0, current_stock_kg=5100.0, 
                              location='Secondary Warehouse Section B'),
                    StorageArea(name='Premium Storage', capacity_kg=5000.0, current_stock_kg=3500.0, 
                              location='Premium Products Section'),
                    StorageArea(name='By-products Storage', capacity_kg=4000.0, current_stock_kg=2800.0, 
                              location='By-products Section')
                ]
                db.session.add_all(storage_areas)
                db.session.commit()
                print("✓ Storage areas created")

            # 9. Create Vehicles with Comprehensive Data
            print("🚛 Creating vehicles...")
            if not Vehicle.query.first():
                vehicles = [
                    Vehicle(vehicle_number='RJ-14-AB-1234', supplier_id=1, driver_name='Ram Singh', 
                           driver_phone='9876543230', arrival_time=datetime.now() - timedelta(hours=3), 
                           status='unloaded', final_weight=2500.0, quality_category='Premium'),
                    Vehicle(vehicle_number='PB-02-CD-5678', supplier_id=2, driver_name='Harpreet Singh', 
                           driver_phone='9876543231', arrival_time=datetime.now() - timedelta(hours=2), 
                           status='quality_check', final_weight=3200.0, quality_category='Standard'),
                    Vehicle(vehicle_number='MP-15-EF-9012', supplier_id=3, driver_name='Ravi Kumar', 
                           driver_phone='9876543232', arrival_time=datetime.now() - timedelta(hours=1), 
                           status='approved', final_weight=2800.0, quality_category='Standard'),
                    Vehicle(vehicle_number='UP-09-GH-3456', supplier_id=4, driver_name='Suresh Gupta', 
                           driver_phone='9876543233', arrival_time=datetime.now() - timedelta(minutes=45), 
                           status='pending', final_weight=3100.0),
                    Vehicle(vehicle_number='HR-10-IJ-7890', supplier_id=5, driver_name='Vikram Singh', 
                           driver_phone='9876543234', arrival_time=datetime.now() - timedelta(minutes=30), 
                           status='pending', final_weight=2900.0),
                    Vehicle(vehicle_number='RJ-14-KL-2468', supplier_id=1, driver_name='Mohan Lal', 
                           driver_phone='9876543235', arrival_time=datetime.now() - timedelta(minutes=15), 
                           status='pending', final_weight=2750.0)
                ]
                db.session.add_all(vehicles)
                db.session.commit()
                print("✓ Vehicles created")

            # 10. Create Quality Tests
            print("🔬 Creating quality tests...")
            if not QualityTest.query.first():
                quality_tests = [
                    QualityTest(vehicle_id=1, sample_bags_tested=5, total_bags=50, category_assigned='Premium', 
                               moisture_content=11.5, lab_instructor='Dr. Sharma', approved=True, test_weight=78.5,
                               protein=12.8, gluten=28.5, falling_number=350),
                    QualityTest(vehicle_id=2, sample_bags_tested=4, total_bags=64, category_assigned='Standard', 
                               moisture_content=12.8, lab_instructor='Dr. Patel', approved=True, test_weight=76.2,
                               protein=11.5, gluten=25.3, falling_number=320),
                    QualityTest(vehicle_id=3, sample_bags_tested=3, total_bags=56, category_assigned='Standard', 
                               moisture_content=13.1, lab_instructor='Dr. Singh', approved=True, test_weight=75.8,
                               protein=11.2, gluten=24.7, falling_number=310)
                ]
                db.session.add_all(quality_tests)
                db.session.commit()
                print("✓ Quality tests created")

            # 11. Create Production Orders
            print("🏭 Creating production orders...")
            if not ProductionOrder.query.first():
                production_orders = [
                    ProductionOrder(order_number='PRO-2025-001', customer_id=1, product_id=1, quantity=1000.0, 
                                   status='completed', priority='high', created_by='Production Manager',
                                   target_completion=datetime.now() + timedelta(days=2), finished_good_type='Premium Maida'),
                    ProductionOrder(order_number='PRO-2025-002', customer_id=2, product_id=2, quantity=1500.0, 
                                   status='cleaning', priority='normal', created_by='Production Manager',
                                   target_completion=datetime.now() + timedelta(days=3), finished_good_type='Standard Maida'),
                    ProductionOrder(order_number='PRO-2025-003', customer_id=3, product_id=3, quantity=800.0, 
                                   status='planning', priority='normal', created_by='Production Manager',
                                   target_completion=datetime.now() + timedelta(days=4), finished_good_type='Suji'),
                    ProductionOrder(order_number='PRO-2025-004', customer_id=4, product_id=5, quantity=1200.0, 
                                   status='pending', priority='low', created_by='Production Manager',
                                   target_completion=datetime.now() + timedelta(days=5), finished_good_type='Chakki Atta'),
                    ProductionOrder(order_number='PRO-2025-005', customer_id=5, product_id=1, quantity=900.0, 
                                   status='24h_completed', priority='high', created_by='Production Manager',
                                   target_completion=datetime.now() + timedelta(days=3), finished_good_type='Premium Maida')
                ]
                db.session.add_all(production_orders)
                db.session.commit()
                print("✓ Production orders created")

            # 12. Create Production Plans
            print("📋 Creating production plans...")
            production_plans = [
                ProductionPlan(order_id=1, total_percentage=100.0, is_locked=True, created_by='Production Planner'),
                ProductionPlan(order_id=2, total_percentage=100.0, is_locked=False, created_by='Production Planner'),
                ProductionPlan(order_id=3, total_percentage=100.0, is_locked=False, created_by='Production Planner')
            ]
            db.session.add_all(production_plans)
            db.session.commit()

            # Create Production Plan Items
            plan_items = [
                # Plan 1 items (Order 1)
                ProductionPlanItem(plan_id=1, precleaning_bin_id=1, percentage=40.0, calculated_tons=400.0),
                ProductionPlanItem(plan_id=1, precleaning_bin_id=2, percentage=35.0, calculated_tons=350.0),
                ProductionPlanItem(plan_id=1, precleaning_bin_id=3, percentage=25.0, calculated_tons=250.0),
                # Plan 2 items (Order 2)
                ProductionPlanItem(plan_id=2, precleaning_bin_id=4, percentage=50.0, calculated_tons=750.0),
                ProductionPlanItem(plan_id=2, precleaning_bin_id=5, percentage=30.0, calculated_tons=450.0),
                ProductionPlanItem(plan_id=2, precleaning_bin_id=6, percentage=20.0, calculated_tons=300.0),
                # Plan 3 items (Order 3)
                ProductionPlanItem(plan_id=3, precleaning_bin_id=7, percentage=60.0, calculated_tons=480.0),
                ProductionPlanItem(plan_id=3, precleaning_bin_id=8, percentage=40.0, calculated_tons=320.0)
            ]
            db.session.add_all(plan_items)
            db.session.commit()
            print("✓ Production plans and items created")

            # 13. Create Cleaning Processes
            print("🧽 Creating cleaning processes...")
            cleaning_processes = [
                CleaningProcess(order_id=2, cleaning_bin_id=2, process_type='24_hour', duration_hours=24.0,
                               start_time=datetime.now() - timedelta(hours=10), 
                               end_time=datetime.now() + timedelta(hours=14),
                               status='running', operator_name='Cleaning Operator 1', machine_name='24-Hour Cleaner A',
                               timer_active=True, countdown_start=datetime.now() - timedelta(hours=10),
                               countdown_end=datetime.now() + timedelta(hours=14)),
                CleaningProcess(order_id=5, cleaning_bin_id=5, process_type='12_hour', duration_hours=12.0,
                               start_time=datetime.now() - timedelta(hours=8), 
                               end_time=datetime.now() + timedelta(hours=4),
                               status='running', operator_name='Cleaning Operator 2', machine_name='12-Hour Cleaner B',
                               timer_active=True, countdown_start=datetime.now() - timedelta(hours=8),
                               countdown_end=datetime.now() + timedelta(hours=4),
                               start_moisture=14.5, target_moisture=12.0)
            ]
            db.session.add_all(cleaning_processes)
            db.session.commit()
            print("✓ Cleaning processes created")

            # 14. Create Finished Goods
            print("📦 Creating finished goods...")
            finished_goods = [
                FinishedGoods(order_id=1, product_id=1, quantity=950.0, storage_type='bags', 
                             bag_weight=50.0, bag_count=19, batch_number='BATCH-PRO-2025-001-20250909',
                             storage_id=1),
                FinishedGoods(order_id=1, product_id=7, quantity=50.0, storage_type='bulk', 
                             batch_number='BATCH-PRO-2025-001-BRAN-20250909', storage_id=6),
                FinishedGoods(order_id=2, product_id=2, quantity=1200.0, storage_type='bags', 
                             bag_weight=25.0, bag_count=48, batch_number='BATCH-PRO-2025-002-20250909',
                             storage_id=2)
            ]
            db.session.add_all(finished_goods)
            db.session.commit()
            print("✓ Finished goods created")

            # 15. Create Sales Orders
            print("💼 Creating sales orders...")
            sales_orders = [
                SalesOrder(order_number='SO-2025-001', customer_id=1, salesman='Sales Rep 1',
                          delivery_date=datetime.now() + timedelta(days=7), total_quantity=500.0,
                          delivered_quantity=0.0, pending_quantity=500.0, status='pending'),
                SalesOrder(order_number='SO-2025-002', customer_id=2, salesman='Sales Rep 2',
                          delivery_date=datetime.now() + timedelta(days=5), total_quantity=800.0,
                          delivered_quantity=200.0, pending_quantity=600.0, status='partial'),
                SalesOrder(order_number='SO-2025-003', customer_id=3, salesman='Sales Rep 3',
                          delivery_date=datetime.now() + timedelta(days=10), total_quantity=1000.0,
                          delivered_quantity=1000.0, pending_quantity=0.0, status='completed')
            ]
            db.session.add_all(sales_orders)
            db.session.commit()
            print("✓ Sales orders created")

            # 16. Create Dispatch Vehicles
            print("🚛 Creating dispatch vehicles...")
            dispatch_vehicles = [
                DispatchVehicle(vehicle_number='DL-01-AB-1111', driver_name='Delivery Driver 1', 
                               driver_phone='9876543241', state='Delhi', city='Delhi', capacity=5000.0, status='available'),
                DispatchVehicle(vehicle_number='MH-02-CD-2222', driver_name='Delivery Driver 2', 
                               driver_phone='9876543242', state='Maharashtra', city='Mumbai', capacity=4500.0, status='available'),
                DispatchVehicle(vehicle_number='KA-03-EF-3333', driver_name='Delivery Driver 3', 
                               driver_phone='9876543243', state='Karnataka', city='Bangalore', capacity=5500.0, status='dispatched')
            ]
            db.session.add_all(dispatch_vehicles)
            db.session.commit()
            print("✓ Dispatch vehicles created")

            # 17. Create Transfers
            print("↔️ Creating transfer records...")
            transfers = [
                Transfer(from_godown_id=1, to_precleaning_bin_id=1, quantity=125.0, 
                        transfer_type='godown_to_precleaning', operator='Transfer Operator 1',
                        transfer_time=datetime.now() - timedelta(days=2), notes='Regular transfer to pre-cleaning'),
                Transfer(from_godown_id=2, to_precleaning_bin_id=2, quantity=185.0, 
                        transfer_type='godown_to_precleaning', operator='Transfer Operator 2',
                        transfer_time=datetime.now() - timedelta(days=1), notes='Premium wheat transfer'),
                Transfer(from_precleaning_bin_id=1, to_precleaning_bin_id=3, quantity=50.0, 
                        transfer_type='precleaning_to_precleaning', operator='Transfer Operator 1',
                        transfer_time=datetime.now() - timedelta(hours=12), notes='Bin redistribution')
            ]
            db.session.add_all(transfers)
            db.session.commit()
            print("✓ Transfer records created")

            # 18. Create Cleaning Machines
            print("🔧 Creating cleaning machines...")
            cleaning_machines = [
                CleaningMachine(name='Drum Shield #1', machine_type='drum_shield', 
                               cleaning_frequency_hours=3, location='Pre-cleaning Area A',
                               last_cleaned=datetime.now() - timedelta(hours=2)),
                CleaningMachine(name='Magnet Separator #1', machine_type='magnet_separator', 
                               cleaning_frequency_hours=4, location='Pre-cleaning Area B',
                               last_cleaned=datetime.now() - timedelta(hours=3)),
                CleaningMachine(name='Vibro Separator #1', machine_type='vibro_separator', 
                               cleaning_frequency_hours=2, location='Cleaning Area A',
                               last_cleaned=datetime.now() - timedelta(hours=1))
            ]
            db.session.add_all(cleaning_machines)
            db.session.commit()
            print("✓ Cleaning machines created")

            # 19. Create Users
            print("👥 Creating users...")
            if not User.query.first():
                users = [
                    User(username='admin', role='admin', phone='9876543250', is_blocked=False),
                    User(username='production_manager', role='production_manager', phone='9876543251', is_blocked=False),
                    User(username='lab_instructor', role='lab_instructor', phone='9876543252', is_blocked=False),
                    User(username='operator1', role='operator', phone='9876543253', is_blocked=False),
                    User(username='operator2', role='operator', phone='9876543254', is_blocked=False)
                ]
                db.session.add_all(users)
                db.session.commit()
                print("✓ Users created")

            # 20. Create Raw Wheat Quality Reports
            print("📊 Creating quality reports...")
            quality_reports = [
                RawWheatQualityReport(vehicle_id=1, wheat_variety='HD-2967', test_date=datetime.now().date(),
                                     bill_number='BILL-001', lab_chemist='Dr. Sharma', moisture=11.5,
                                     hectoliter_weight=78.5, wet_gluten=28.5, dry_gluten=9.2,
                                     category_assigned='Premium', approved=True),
                RawWheatQualityReport(vehicle_id=2, wheat_variety='PBW-725', test_date=datetime.now().date(),
                                     bill_number='BILL-002', lab_chemist='Dr. Patel', moisture=12.8,
                                     hectoliter_weight=76.2, wet_gluten=25.3, dry_gluten=8.5,
                                     category_assigned='Standard', approved=True)
            ]
            db.session.add_all(quality_reports)
            db.session.commit()
            print("✓ Quality reports created")

            # Update stock levels based on transfers
            print("📊 Updating stock levels...")
            
            # Update godown stocks after transfers
            godown1 = Godown.query.get(1)
            godown2 = Godown.query.get(2)
            if godown1:
                godown1.current_stock -= 125.0  # Transfer to precleaning bin 1
            if godown2:
                godown2.current_stock -= 185.0  # Transfer to precleaning bin 2
                
            db.session.commit()
            
            print("\n🎉 COMPREHENSIVE DATA POPULATION COMPLETED! 🎉")
            print("=" * 60)
            print("📈 Summary of created records:")
            print(f"   👥 Suppliers: {Supplier.query.count()}")
            print(f"   🏢 Customers: {Customer.query.count()}")
            print(f"   📦 Products: {Product.query.count()}")
            print(f"   🏭 Godowns: {Godown.query.count()}")
            print(f"   🔄 Pre-cleaning Bins: {PrecleaningBin.query.count()}")
            print(f"   🧹 Cleaning Bins: {CleaningBin.query.count()}")
            print(f"   📦 Storage Areas: {StorageArea.query.count()}")
            print(f"   🚛 Vehicles: {Vehicle.query.count()}")
            print(f"   🔬 Quality Tests: {QualityTest.query.count()}")
            print(f"   🏭 Production Orders: {ProductionOrder.query.count()}")
            print(f"   📋 Production Plans: {ProductionPlan.query.count()}")
            print(f"   🧽 Cleaning Processes: {CleaningProcess.query.count()}")
            print(f"   📦 Finished Goods: {FinishedGoods.query.count()}")
            print(f"   💼 Sales Orders: {SalesOrder.query.count()}")
            print(f"   🚛 Dispatch Vehicles: {DispatchVehicle.query.count()}")
            print(f"   ↔️ Transfers: {Transfer.query.count()}")
            print(f"   👥 Users: {User.query.count()}")
            print("=" * 60)
            print("✅ Your wheat processing system is now fully populated with realistic data!")
            print("🌾 Ready for production operations!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during data population: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    populate_all_tables()
