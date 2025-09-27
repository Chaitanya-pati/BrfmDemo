#!/usr/bin/env python3
"""
Clean dummy data population script for the wheat processing application.
Only populates essential logistics data (no production functionality).
"""

from datetime import datetime, timedelta
import random
from app import app, db
from models import (
    Supplier, GodownType, Godown, PrecleaningBin, Product, Customer, 
    Vehicle, QualityTest, Transfer, SalesOrder, SalesOrderItem, 
    DispatchVehicle, Dispatch, DispatchItem, User
)

def populate_dummy_data():
    """Populate all tables with comprehensive dummy data for essential logistics"""
    with app.app_context():
        try:
            # Clear existing data
            print("Clearing existing data...")
            db.session.query(DispatchItem).delete()
            db.session.query(Dispatch).delete()
            db.session.query(SalesOrderItem).delete()
            db.session.query(SalesOrder).delete()
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
                    company_name='Rajasthan Agricultural Co.',
                    contact_person='Vikram Singh',
                    phone='9876543213',
                    address='Agriculture Market Yard',
                    city='Jaipur',
                    state='Rajasthan',
                    postal_code='302001'
                ),
                Supplier(
                    company_name='MP Grain Dealers',
                    contact_person='Anand Verma',
                    phone='9876543214',
                    address='Krishi Upaj Mandi',
                    city='Indore',
                    state='Madhya Pradesh',
                    postal_code='452001'
                )
            ]
            db.session.add_all(suppliers)
            db.session.commit()
            print("✓ Suppliers created")

            # 2. Create Customers
            print("Creating customers...")
            customers = [
                Customer(
                    company_name='Delhi Flour Mills Pvt Ltd',
                    contact_person='Rakesh Sharma',
                    phone='9876543220',
                    email='rakesh@delhiflour.com',
                    address='Industrial Area Phase-I',
                    city='Delhi',
                    state='Delhi',
                    postal_code='110001'
                ),
                Customer(
                    company_name='Mumbai Food Processing Co.',
                    contact_person='Amit Patel',
                    phone='9876543221',
                    email='amit@mumbaiFood.com',
                    address='Andheri Industrial Estate',
                    city='Mumbai',
                    state='Maharashtra',
                    postal_code='400001'
                ),
                Customer(
                    company_name='Bangalore Bakery Chain',
                    contact_person='Suresh Kumar',
                    phone='9876543222',
                    email='suresh@bangalorebakery.com',
                    address='Electronic City Phase-II',
                    city='Bangalore',
                    state='Karnataka',
                    postal_code='560001'
                ),
                Customer(
                    company_name='Chennai Food Industries',
                    contact_person='Raman Iyer',
                    phone='9876543223',
                    email='raman@chennaifood.com',
                    address='Ambattur Industrial Estate',
                    city='Chennai',
                    state='Tamil Nadu',
                    postal_code='600001'
                ),
                Customer(
                    company_name='Kolkata Grain Products',
                    contact_person='Debabrata Das',
                    phone='9876543224',
                    email='debabrata@kolkatagrain.com',
                    address='Kasba Industrial Area',
                    city='Kolkata',
                    state='West Bengal',
                    postal_code='700001'
                )
            ]
            db.session.add_all(customers)
            db.session.commit()
            print("✓ Customers created")

            # 3. Create Products
            print("Creating products...")
            products = [
                Product(name='Premium Maida', category='Main Product', description='High quality all-purpose flour'),
                Product(name='Fine Suji', category='Main Product', description='Premium semolina'),
                Product(name='Chakki Fresh Atta', category='Main Product', description='Fresh stone-ground whole wheat flour'),
                Product(name='Wheat Bran', category='Bran', description='Nutritious wheat bran'),
                Product(name='Coarse Suji', category='Main Product', description='Coarse semolina for special use'),
                Product(name='Refined Flour', category='Main Product', description='Highly refined wheat flour')
            ]
            db.session.add_all(products)
            db.session.commit()
            print("✓ Products created")

            # 4. Create comprehensive vehicles with quality tests
            print("Creating vehicles with quality tests...")
            vehicles_data = [
                {
                    'vehicle_number': f'PB{str(i+10).zfill(2)}AB{random.randint(1000, 9999)}',
                    'supplier_id': random.randint(1, 5),
                    'driver_name': f'Driver {i+1}',
                    'driver_phone': f'987654{str(i+3210).zfill(4)}',
                    'arrival_time': datetime.now() - timedelta(days=random.randint(0, 7), hours=random.randint(1, 12)),
                    'status': random.choice(['pending', 'quality_check', 'approved', 'rejected']),
                    'quality_category': random.choice(['mill', 'low mill', 'hd']),
                    'net_weight_before': random.uniform(3000, 8000),
                    'godown_id': random.randint(1, 4) if random.choice([True, False]) else None
                }
                for i in range(15)
            ]
            
            for vehicle_data in vehicles_data:
                vehicle_data['net_weight_after'] = vehicle_data['net_weight_before'] - random.uniform(50, 200)
                vehicle_data['final_weight'] = vehicle_data['net_weight_after']
                
                vehicle = Vehicle(**vehicle_data)
                db.session.add(vehicle)
                db.session.flush()  # Get the vehicle ID
                
                # Create quality test for approved/rejected vehicles
                if vehicle.status in ['approved', 'rejected']:
                    quality_test = QualityTest(
                        vehicle_id=vehicle.id,
                        sample_bags_tested=random.randint(3, 10),
                        total_bags=random.randint(50, 200),
                        category_assigned=vehicle.quality_category,
                        moisture_content=random.uniform(10.0, 15.0),
                        foreign_matter=random.uniform(0.5, 3.0),
                        broken_grains=random.uniform(1.0, 5.0),
                        test_result='Approved' if vehicle.status == 'approved' else 'Rejected',
                        tested_by=f'Lab Tech {random.randint(1, 3)}',
                        test_time=vehicle.arrival_time + timedelta(hours=random.randint(1, 4)),
                        approved=vehicle.status == 'approved'
                    )
                    db.session.add(quality_test)
            
            db.session.commit()
            print("✓ Vehicles and quality tests created")

            # 5. Create comprehensive sales orders
            print("Creating sales orders...")
            sales_orders_data = [
                {
                    'order_number': f'SO{str(i+1).zfill(4)}',
                    'customer_id': random.randint(1, 5),
                    'salesman': f'Sales Rep {random.randint(1, 5)}',
                    'order_date': datetime.now() - timedelta(days=random.randint(0, 30)),
                    'total_quantity': random.uniform(500, 2000),
                    'status': random.choice(['pending', 'partial', 'completed'])
                }
                for i in range(20)
            ]
            
            for order_data in sales_orders_data:
                delivered = random.uniform(0, order_data['total_quantity']) if order_data['status'] != 'pending' else 0
                if order_data['status'] == 'completed':
                    delivered = order_data['total_quantity']
                
                order_data['delivered_quantity'] = delivered
                order_data['pending_quantity'] = order_data['total_quantity'] - delivered
                
                sales_order = SalesOrder(**order_data)
                db.session.add(sales_order)
                db.session.flush()
                
                # Create order items
                num_items = random.randint(1, 3)
                remaining_qty = sales_order.total_quantity
                
                for item_idx in range(num_items):
                    if item_idx == num_items - 1:
                        item_qty = remaining_qty
                    else:
                        item_qty = random.uniform(100, remaining_qty * 0.6)
                        remaining_qty -= item_qty
                    
                    delivered_item = (item_qty / sales_order.total_quantity) * sales_order.delivered_quantity
                    
                    order_item = SalesOrderItem(
                        sales_order_id=sales_order.id,
                        product_id=random.randint(1, 6),
                        quantity=item_qty,
                        delivered_quantity=delivered_item,
                        pending_quantity=item_qty - delivered_item
                    )
                    db.session.add(order_item)
            
            db.session.commit()
            print("✓ Sales orders and items created")

            # 6. Create dispatch vehicles
            print("Creating dispatch vehicles...")
            dispatch_vehicles = [
                DispatchVehicle(
                    vehicle_number=f'DL{str(i+1).zfill(2)}CD{random.randint(1000, 9999)}',
                    driver_name=f'Dispatch Driver {i+1}',
                    driver_phone=f'987654{str(i+5000).zfill(4)}',
                    state=random.choice(['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Punjab']),
                    city=random.choice(['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Ludhiana']),
                    capacity=random.uniform(5000, 12000),
                    status=random.choice(['available', 'dispatched', 'blocked'])
                )
                for i in range(10)
            ]
            db.session.add_all(dispatch_vehicles)
            db.session.commit()
            print("✓ Dispatch vehicles created")

            # 7. Create some dispatches for completed orders
            print("Creating dispatches...")
            completed_orders = SalesOrder.query.filter(
                SalesOrder.delivered_quantity > 0
            ).limit(10).all()
            
            available_vehicles = DispatchVehicle.query.filter_by(status='available').all()
            
            for i, order in enumerate(completed_orders[:len(available_vehicles)]):
                vehicle = available_vehicles[i]
                dispatch = Dispatch(
                    dispatch_number=f'DP{str(i+1).zfill(4)}',
                    sales_order_id=order.id,
                    vehicle_id=vehicle.id,
                    dispatch_date=order.order_date + timedelta(days=random.randint(1, 5)),
                    quantity=min(order.delivered_quantity, vehicle.capacity),
                    status=random.choice(['loaded', 'in_transit', 'delivered']),
                    delivered_by=f'Delivery Person {random.randint(1, 5)}'
                )
                
                if dispatch.status == 'delivered':
                    dispatch.delivery_date = dispatch.dispatch_date + timedelta(days=random.randint(1, 3))
                
                db.session.add(dispatch)
                db.session.flush()
                
                # Create dispatch items
                order_items = SalesOrderItem.query.filter_by(sales_order_id=order.id).all()
                for item in order_items:
                    if item.delivered_quantity > 0:
                        dispatch_item = DispatchItem(
                            dispatch_id=dispatch.id,
                            product_id=item.product_id,
                            quantity=item.delivered_quantity,
                            bag_count=int(item.delivered_quantity / 50)  # Assuming 50kg bags
                        )
                        db.session.add(dispatch_item)
                
                # Update vehicle status
                if dispatch.status != 'delivered':
                    vehicle.status = 'dispatched'
            
            db.session.commit()
            print("✓ Dispatches created")

            # 8. Create transfers (godown to precleaning)
            print("Creating transfers...")
            godowns = Godown.query.filter(Godown.current_stock > 0).all()
            precleaning_bins = PrecleaningBin.query.all()
            
            for i in range(8):
                from_godown = random.choice(godowns)
                to_bin = random.choice(precleaning_bins)
                transfer_qty = random.uniform(10, min(50, from_godown.current_stock))
                
                transfer = Transfer(
                    from_godown_id=from_godown.id,
                    to_precleaning_bin_id=to_bin.id,
                    quantity=transfer_qty,
                    transfer_time=datetime.now() - timedelta(days=random.randint(0, 5)),
                    transfer_type='godown_to_precleaning',
                    operator=f'Operator {random.randint(1, 3)}',
                    notes=f'Transfer {i+1} from {from_godown.name} to {to_bin.name}'
                )
                db.session.add(transfer)
                
                # Update stock levels
                from_godown.current_stock -= transfer_qty
                to_bin.current_stock += transfer_qty
            
            db.session.commit()
            print("✓ Transfers created")

            # 9. Create users
            print("Creating users...")
            if not User.query.first():
                users = [
                    User(username='admin', role='admin', phone='9876543300'),
                    User(username='operator1', role='operator', phone='9876543301'),
                    User(username='operator2', role='operator', phone='9876543302'),
                    User(username='lab_tech1', role='lab_instructor', phone='9876543303'),
                    User(username='lab_tech2', role='lab_instructor', phone='9876543304'),
                    User(username='supervisor', role='admin', phone='9876543305')
                ]
                db.session.add_all(users)
                db.session.commit()
                print("✓ Users created")

            print("✅ All dummy data populated successfully!")
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
            print(f"  - {SalesOrderItem.query.count()} sales order items")
            print(f"  - {DispatchVehicle.query.count()} dispatch vehicles")
            print(f"  - {Dispatch.query.count()} dispatches")
            print(f"  - {Transfer.query.count()} transfers")
            print(f"  - {User.query.count()} users")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error populating dummy data: {e}")
            raise

if __name__ == "__main__":
    populate_dummy_data()