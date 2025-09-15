
#!/usr/bin/env python3
"""
Script to create approved vehicles for weight entry testing
"""

from app import app, db
from models import Vehicle, Supplier
from datetime import datetime, timedelta
import random

def create_approved_vehicles():
    """Create some approved vehicles for testing weight entry"""
    with app.app_context():
        try:
            print("🚛 Creating approved vehicles for weight entry testing...")
            
            # Get existing suppliers
            suppliers = Supplier.query.all()
            if not suppliers:
                print("❌ No suppliers found. Please run populate_all_tables.py first.")
                return
            
            # Create 5 approved vehicles
            approved_vehicles = []
            for i in range(5):
                vehicle = Vehicle(
                    vehicle_number=f'AP{15+i}CD{2000+i}',
                    supplier_id=random.choice(suppliers).id,
                    driver_name=f'Approved Driver {i+1}',
                    driver_phone=f'987654{4000+i}',
                    arrival_time=datetime.now() - timedelta(days=random.randint(1, 5)),
                    entry_time=datetime.now() - timedelta(days=random.randint(1, 5)),
                    status='approved',  # Set status as approved
                    quality_category=random.choice(['Mill', 'Low Mill', 'HD']),
                    owner_approved=True,  # Set owner_approved as True
                    net_weight_before=random.uniform(28000, 35000),
                    net_weight_after=0  # Will be filled during weight entry
                )
                approved_vehicles.append(vehicle)
            
            db.session.add_all(approved_vehicles)
            db.session.commit()
            
            print("✅ Successfully created approved vehicles:")
            for vehicle in approved_vehicles:
                print(f"   📋 {vehicle.vehicle_number} - {vehicle.supplier.company_name} - Status: {vehicle.status} - Owner Approved: {vehicle.owner_approved}")
            
            # Also update some existing vehicles to approved status
            existing_vehicles = Vehicle.query.filter_by(status='quality_check').limit(3).all()
            for vehicle in existing_vehicles:
                vehicle.status = 'approved'
                vehicle.owner_approved = True
            
            db.session.commit()
            
            if existing_vehicles:
                print(f"\n✅ Updated {len(existing_vehicles)} existing vehicles to approved status")
            
            # Show total approved vehicles
            total_approved = Vehicle.query.filter_by(status='approved', owner_approved=True).count()
            print(f"\n🎉 Total approved vehicles available for weight entry: {total_approved}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating approved vehicles: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_approved_vehicles()
