#!/usr/bin/env python3
"""
Clean data population script for the wheat processing application.
Only populates essential logistics data (no production functionality).
"""

import os
from datetime import datetime, timedelta
import random
from app import app, db
from models import (
    Supplier, GodownType, Godown, PrecleaningBin, Product, Customer, 
    Vehicle, QualityTest, Transfer, SalesOrder, SalesOrderItem, 
    DispatchVehicle, Dispatch, DispatchItem, User
)

def populate_all_tables():
    """Populate all tables with essential sample data"""
    with app.app_context():
        try:
            print("🌾 Starting essential data population for wheat processing system...")
            
            # Clear existing data first
            print("🗑️ Clearing existing data...")
            db.session.query(DispatchItem).delete()
            db.session.query(Dispatch).delete()
            db.session.query(SalesOrderItem).delete()
            db.session.query(SalesOrder).delete()
            db.session.query(Transfer).delete()
            db.session.query(QualityTest).delete()
            db.session.query(Vehicle).delete()
            db.session.commit()

            # 1. Create Suppliers
            print("📦 Creating suppliers...")
            if not Supplier.query.first():
                suppliers = [
                    Supplier(
                        company_name='Rajasthan Wheat Co.',
                        contact_person='Rajesh Kumar',
                        phone='9876543210',
                        city='Jaipur',
                        address='123 Grain Market, Jaipur',
                        state='Rajasthan',
                        postal_code='302001'
                    ),
                    Supplier(
                        company_name='Punjab Agro Traders',
                        contact_person='Harpreet Singh',
                        phone='9876543211',
                        city='Ludhiana',
                        address='456 Mandi Road, Ludhiana',
                        state='Punjab',
                        postal_code='141001'
                    ),
                    Supplier(
                        company_name='MP Wheat Suppliers',
                        contact_person='Ravi Sharma',
                        phone='9876543212',
                        city='Indore',
                        address='789 Krishi Upaj Mandi, Indore',
                        state='Madhya Pradesh',
                        postal_code='452001'
                    )
                ]
                db.session.add_all(suppliers)
                db.session.commit()
                print("✓ Suppliers created")

            # 2. Create Customers
            print("🏢 Creating customers...")
            if not Customer.query.first():
                customers = [
                    Customer(
                        company_name='Delhi Bakery Chain',
                        contact_person='Mohan Lal',
                        phone='9876543220',
                        city='Delhi',
                        address='100 Connaught Place, Delhi',
                        state='Delhi',
                        postal_code='110001'
                    ),
                    Customer(
                        company_name='Mumbai Food Industries',
                        contact_person='Anil Patel',
                        phone='9876543221',
                        city='Mumbai',
                        address='200 Industrial Estate, Mumbai',
                        state='Maharashtra',
                        postal_code='400001'
                    ),
                    Customer(
                        company_name='Bangalore Flour Mills',
                        contact_person='Sunil Kumar',
                        phone='9876543222',
                        city='Bangalore',
                        address='300 Electronic City, Bangalore',
                        state='Karnataka',
                        postal_code='560001'
                    )
                ]
                db.session.add_all(customers)
                db.session.commit()
                print("✓ Customers created")

            # 3. Create Products
            print("🌾 Creating products...")
            if not Product.query.first():
                products = [
                    Product(name='Maida (All Purpose Flour)', category='Main Product', description='Fine wheat flour'),
                    Product(name='Suji (Semolina)', category='Main Product', description='Coarse wheat flour'),
                    Product(name='Chakki Atta', category='Main Product', description='Whole wheat flour'),
                    Product(name='Bran', category='Bran', description='Wheat bran')
                ]
                db.session.add_all(products)
                db.session.commit()
                print("✓ Products created")

            # 4. Create Godown Types
            print("🏭 Creating godown types...")
            if not GodownType.query.first():
                godown_types = [
                    GodownType(name='Mill', description='Regular mill quality wheat'),
                    GodownType(name='Low Mill', description='Lower quality wheat'),
                    GodownType(name='HD', description='High density wheat')
                ]
                db.session.add_all(godown_types)
                db.session.commit()
                print("✓ Godown types created")

            # 5. Create Godowns
            print("🏪 Creating godowns...")
            if not Godown.query.first():
                godowns = [
                    Godown(name='Godown A', type_id=1, capacity=100.0, current_stock=75.5),
                    Godown(name='Godown B', type_id=2, capacity=150.0, current_stock=120.0),
                    Godown(name='Godown C', type_id=3, capacity=200.0, current_stock=180.3),
                    Godown(name='Godown D', type_id=1, capacity=175.0, current_stock=95.2)
                ]
                db.session.add_all(godowns)
                db.session.commit()
                print("✓ Godowns created")

            # 6. Create Precleaning Bins
            print("🧽 Creating precleaning bins...")
            if not PrecleaningBin.query.first():
                bins = [
                    PrecleaningBin(name='Pre-cleaning Bin 1', capacity=50.0, current_stock=35.0),
                    PrecleaningBin(name='Pre-cleaning Bin 2', capacity=75.0, current_stock=60.5),
                    PrecleaningBin(name='Pre-cleaning Bin 3', capacity=60.0, current_stock=45.0)
                ]
                db.session.add_all(bins)
                db.session.commit()
                print("✓ Precleaning bins created")

            # 7. Create Vehicles
            print("🚛 Creating vehicles...")
            vehicles = [
                Vehicle(
                    vehicle_number='RJ01AB1234',
                    supplier_id=1,
                    driver_name='Ram Singh',
                    driver_phone='9876543230',
                    arrival_time=datetime.now() - timedelta(hours=2),
                    status='approved',
                    quality_category='mill',
                    net_weight_before=5000.0,
                    net_weight_after=4950.0,
                    final_weight=4950.0,
                    godown_id=1
                ),
                Vehicle(
                    vehicle_number='PB02CD5678',
                    supplier_id=2,
                    driver_name='Harpal Singh',
                    driver_phone='9876543231',
                    arrival_time=datetime.now() - timedelta(hours=1),
                    status='quality_check',
                    quality_category='hd',
                    net_weight_before=7500.0,
                    godown_id=3
                )
            ]
            db.session.add_all(vehicles)
            db.session.commit()
            print("✓ Vehicles created")

            # 8. Create Quality Tests
            print("🔬 Creating quality tests...")
            quality_tests = [
                QualityTest(
                    vehicle_id=1,
                    sample_bags_tested=5,
                    total_bags=100,
                    category_assigned='mill',
                    moisture_content=12.5,
                    foreign_matter=1.2,
                    test_result='Approved',
                    tested_by='Lab Technician 1',
                    test_time=datetime.now() - timedelta(hours=1, minutes=30),
                    approved=True
                ),
                QualityTest(
                    vehicle_id=2,
                    sample_bags_tested=3,
                    total_bags=150,
                    category_assigned='hd',
                    moisture_content=11.8,
                    foreign_matter=0.9,
                    test_result='Under Review',
                    tested_by='Lab Technician 2',
                    test_time=datetime.now() - timedelta(minutes=30),
                    approved=False
                )
            ]
            db.session.add_all(quality_tests)
            db.session.commit()
            print("✓ Quality tests created")

            # 9. Create Sales Orders
            print("💼 Creating sales orders...")
            sales_orders = [
                SalesOrder(
                    order_number='SO001',
                    customer_id=1,
                    salesman='Sales Rep 1',
                    order_date=datetime.now() - timedelta(days=1),
                    total_quantity=1000.0,
                    delivered_quantity=500.0,
                    pending_quantity=500.0,
                    status='partial'
                ),
                SalesOrder(
                    order_number='SO002',
                    customer_id=2,
                    salesman='Sales Rep 2',
                    order_date=datetime.now(),
                    total_quantity=750.0,
                    delivered_quantity=0.0,
                    pending_quantity=750.0,
                    status='pending'
                )
            ]
            db.session.add_all(sales_orders)
            db.session.commit()
            print("✓ Sales orders created")

            # 10. Create Sales Order Items
            print("📋 Creating sales order items...")
            order_items = [
                SalesOrderItem(
                    sales_order_id=1,
                    product_id=1,
                    quantity=600.0,
                    delivered_quantity=300.0,
                    pending_quantity=300.0
                ),
                SalesOrderItem(
                    sales_order_id=1,
                    product_id=4,
                    quantity=400.0,
                    delivered_quantity=200.0,
                    pending_quantity=200.0
                ),
                SalesOrderItem(
                    sales_order_id=2,
                    product_id=2,
                    quantity=750.0,
                    delivered_quantity=0.0,
                    pending_quantity=750.0
                )
            ]
            db.session.add_all(order_items)
            db.session.commit()
            print("✓ Sales order items created")

            # 11. Create Dispatch Vehicles
            print("🚛 Creating dispatch vehicles...")
            dispatch_vehicles = [
                DispatchVehicle(
                    vehicle_number='DL01EF9012',
                    driver_name='Ramesh Kumar',
                    driver_phone='9876543240',
                    state='Delhi',
                    city='Delhi',
                    capacity=10000.0,
                    status='available'
                ),
                DispatchVehicle(
                    vehicle_number='MH02GH3456',
                    driver_name='Suresh Patel',
                    driver_phone='9876543241',
                    state='Maharashtra',
                    city='Mumbai',
                    capacity=8000.0,
                    status='dispatched'
                )
            ]
            db.session.add_all(dispatch_vehicles)
            db.session.commit()
            print("✓ Dispatch vehicles created")

            # 12. Create Users
            print("👥 Creating users...")
            if not User.query.first():
                users = [
                    User(username='admin', role='admin', phone='9876543250'),
                    User(username='operator1', role='operator', phone='9876543251'),
                    User(username='lab_tech1', role='lab_instructor', phone='9876543252')
                ]
                db.session.add_all(users)
                db.session.commit()
                print("✓ Users created")

            print("✅ All essential data populated successfully!")
            print("Summary:")
            print(f"  - {Supplier.query.count()} suppliers")
            print(f"  - {Customer.query.count()} customers")
            print(f"  - {Product.query.count()} products")
            print(f"  - {GodownType.query.count()} godown types")
            print(f"  - {Godown.query.count()} godowns")
            print(f"  - {PrecleaningBin.query.count()} precleaning bins")
            print(f"  - {Vehicle.query.count()} vehicles")
            print(f"  - {QualityTest.query.count()} quality tests")
            print(f"  - {SalesOrder.query.count()} sales orders")
            print(f"  - {User.query.count()} users")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating data: {e}")
            raise

if __name__ == "__main__":
    populate_all_tables()