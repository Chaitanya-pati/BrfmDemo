
#!/usr/bin/env python3
"""
Add comprehensive godown data with realistic stock levels
"""

from app import app, db
from models import GodownType, Godown
from datetime import datetime
import random

def add_godown_data():
    """Add godown types and godowns with realistic stock data"""
    with app.app_context():
        try:
            print("🏭 Adding comprehensive godown data...")
            
            # Add Godown Types if they don't exist
            if not GodownType.query.first():
                print("📋 Creating godown types...")
                godown_types = [
                    GodownType(name='Premium', description='Premium quality wheat storage'),
                    GodownType(name='Mill', description='Standard mill quality wheat storage'),
                    GodownType(name='Low Mill', description='Lower grade mill wheat storage'),
                    GodownType(name='HD', description='High density wheat storage'),
                    GodownType(name='Organic', description='Certified organic wheat storage'),
                    GodownType(name='Export Quality', description='Export-grade wheat storage'),
                    GodownType(name='Emergency', description='Emergency storage for overflow')
                ]
                db.session.add_all(godown_types)
                db.session.commit()
                print("✓ Godown types created")

            # Clear existing godowns to add fresh data
            existing_godowns = Godown.query.all()
            if existing_godowns:
                print("🗑️ Clearing existing godowns...")
                for godown in existing_godowns:
                    db.session.delete(godown)
                db.session.commit()

            # Add comprehensive godowns with realistic stock
            print("🏗️ Creating godowns with stock data...")
            godowns = [
                # Premium Quality Godowns
                Godown(name='Premium Godown A1', type_id=1, capacity=500.0, current_stock=425.5),
                Godown(name='Premium Godown A2', type_id=1, capacity=450.0, current_stock=380.3),
                Godown(name='Premium Godown A3', type_id=1, capacity=600.0, current_stock=520.7),
                
                # Standard Mill Quality Godowns
                Godown(name='Mill Godown B1', type_id=2, capacity=750.0, current_stock=685.2),
                Godown(name='Mill Godown B2', type_id=2, capacity=800.0, current_stock=725.8),
                Godown(name='Mill Godown B3', type_id=2, capacity=650.0, current_stock=595.4),
                Godown(name='Mill Godown B4', type_id=2, capacity=700.0, current_stock=610.9),
                
                # Low Mill Quality Godowns
                Godown(name='Low Mill Godown C1', type_id=3, capacity=400.0, current_stock=320.5),
                Godown(name='Low Mill Godown C2', type_id=3, capacity=450.0, current_stock=385.7),
                Godown(name='Low Mill Godown C3', type_id=3, capacity=350.0, current_stock=285.3),
                
                # High Density Godowns
                Godown(name='HD Godown D1', type_id=4, capacity=550.0, current_stock=495.6),
                Godown(name='HD Godown D2', type_id=4, capacity=600.0, current_stock=520.8),
                Godown(name='HD Godown D3', type_id=4, capacity=500.0, current_stock=435.2),
                
                # Organic Quality Godowns
                Godown(name='Organic Godown E1', type_id=5, capacity=300.0, current_stock=245.5),
                Godown(name='Organic Godown E2', type_id=5, capacity=350.0, current_stock=285.7),
                
                # Export Quality Godowns
                Godown(name='Export Godown F1', type_id=6, capacity=800.0, current_stock=720.3),
                Godown(name='Export Godown F2', type_id=6, capacity=750.0, current_stock=685.9),
                Godown(name='Export Godown F3', type_id=6, capacity=900.0, current_stock=815.4),
                
                # Emergency Storage
                Godown(name='Emergency Storage G1', type_id=7, capacity=200.0, current_stock=125.8),
                Godown(name='Emergency Storage G2', type_id=7, capacity=250.0, current_stock=180.2)
            ]
            
            db.session.add_all(godowns)
            db.session.commit()
            
            print("\n🎉 GODOWN DATA ADDED SUCCESSFULLY! 🎉")
            print("=" * 50)
            print("📊 Summary:")
            print(f"   🏭 Total Godown Types: {GodownType.query.count()}")
            print(f"   📦 Total Godowns: {Godown.query.count()}")
            print("\n📋 Godown Distribution:")
            
            for godown_type in GodownType.query.all():
                count = Godown.query.filter_by(type_id=godown_type.id).count()
                total_capacity = db.session.query(db.func.sum(Godown.capacity)).filter_by(type_id=godown_type.id).scalar() or 0
                total_stock = db.session.query(db.func.sum(Godown.current_stock)).filter_by(type_id=godown_type.id).scalar() or 0
                utilization = (total_stock / total_capacity * 100) if total_capacity > 0 else 0
                print(f"   {godown_type.name}: {count} godowns, {total_capacity:.1f}T capacity, {total_stock:.1f}T stock ({utilization:.1f}% full)")
            
            # Calculate overall statistics
            total_capacity = db.session.query(db.func.sum(Godown.capacity)).scalar() or 0
            total_stock = db.session.query(db.func.sum(Godown.current_stock)).scalar() or 0
            overall_utilization = (total_stock / total_capacity * 100) if total_capacity > 0 else 0
            
            print("\n🌾 Overall Storage Statistics:")
            print(f"   📊 Total Capacity: {total_capacity:.1f} tons")
            print(f"   📦 Total Current Stock: {total_stock:.1f} tons")
            print(f"   📈 Overall Utilization: {overall_utilization:.1f}%")
            print(f"   🆓 Available Space: {total_capacity - total_stock:.1f} tons")
            print("=" * 50)
            print("✅ Your godowns are now fully populated with realistic stock data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding godown data: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_godown_data()
