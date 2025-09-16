
from app import app, db
from models import *
from datetime import datetime

def fix_sales_dispatch_tables():
    """Fix sales dispatch tables and add sample data"""
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if we have any dispatch vehicles
            vehicle_count = DispatchVehicle.query.count()
            if vehicle_count == 0:
                print("Adding sample dispatch vehicles...")
                
                # Add sample dispatch vehicles
                vehicles = [
                    DispatchVehicle(
                        vehicle_number='TN01AB1234',
                        driver_name='Rajesh Kumar',
                        driver_phone='9876543210',
                        state='Tamil Nadu',
                        city='Chennai',
                        capacity=25.0,
                        status='available'
                    ),
                    DispatchVehicle(
                        vehicle_number='KA02CD5678',
                        driver_name='Suresh Reddy',
                        driver_phone='9876543211',
                        state='Karnataka',
                        city='Bangalore',
                        capacity=30.0,
                        status='available'
                    ),
                    DispatchVehicle(
                        vehicle_number='AP03EF9012',
                        driver_name='Venkat Rao',
                        driver_phone='9876543212',
                        state='Andhra Pradesh',
                        city='Hyderabad',
                        capacity=35.0,
                        status='available'
                    )
                ]
                
                for vehicle in vehicles:
                    db.session.add(vehicle)
                
            # Check if we have customers
            customer_count = Customer.query.count()
            if customer_count == 0:
                print("Adding sample customers...")
                
                customers = [
                    Customer(
                        company_name='ABC Distributors',
                        contact_person='Mr. Sharma',
                        phone='9876543213',
                        email='abc@distributors.com',
                        address='123 Main Street',
                        city='Mumbai',
                        state='Maharashtra',
                        postal_code='400001'
                    ),
                    Customer(
                        company_name='XYZ Wholesale',
                        contact_person='Ms. Patel',
                        phone='9876543214',
                        email='xyz@wholesale.com',
                        address='456 Business Road',
                        city='Delhi',
                        state='Delhi',
                        postal_code='110001'
                    ),
                    Customer(
                        company_name='PQR Traders',
                        contact_person='Mr. Singh',
                        phone='9876543215',
                        email='pqr@traders.com',
                        address='789 Commerce Lane',
                        city='Kolkata',
                        state='West Bengal',
                        postal_code='700001'
                    )
                ]
                
                for customer in customers:
                    db.session.add(customer)
            
            # Check if we have sample sales orders
            sales_order_count = SalesOrder.query.count()
            if sales_order_count == 0:
                print("Adding sample sales orders...")
                
                # Make sure we have customers first
                db.session.commit()
                
                customers = Customer.query.all()
                if customers:
                    for i, customer in enumerate(customers[:2]):  # Add 2 sample orders
                        sales_order = SalesOrder(
                            order_number=f'SO00{i+1}',
                            customer_id=customer.id,
                            salesman=f'Sales Rep {i+1}',
                            total_quantity=50.0 + (i * 25),
                            delivered_quantity=0.0,
                            pending_quantity=50.0 + (i * 25),
                            delivery_date=datetime.now(),
                            status='pending'
                        )
                        db.session.add(sales_order)
            
            db.session.commit()
            print("✅ Sales dispatch tables fixed successfully!")
            
            # Print summary
            print(f"📊 Summary:")
            print(f"   - Customers: {Customer.query.count()}")
            print(f"   - Dispatch Vehicles: {DispatchVehicle.query.count()}")
            print(f"   - Sales Orders: {SalesOrder.query.count()}")
            print(f"   - Dispatches: {Dispatch.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing sales dispatch tables: {e}")

if __name__ == '__main__':
    fix_sales_dispatch_tables()
