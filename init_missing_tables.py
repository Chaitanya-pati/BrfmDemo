
from app import app, db
from models import *

def init_missing_tables():
    """Initialize any missing tables in the database"""
    try:
        with app.app_context():
            # Create all tables that don't exist
            db.create_all()
            print("All missing tables have been created successfully!")
            
            # Check if we need to add some basic data
            if not GodownType.query.first():
                print("Adding basic godown types...")
                godown_types = [
                    GodownType(name='Mill', description='Main mill storage'),
                    GodownType(name='Low Mill', description='Low grade mill storage'),
                    GodownType(name='HD', description='High density storage'),
                    GodownType(name='Durum', description='Durum wheat storage')
                ]
                for gt in godown_types:
                    db.session.add(gt)
                db.session.commit()
                print("Basic godown types added!")
                
            # Add cleaning bins if they don't exist
            if not CleaningBin.query.first():
                print("Adding basic cleaning bins...")
                cleaning_bins = [
                    CleaningBin(name='24-Hour Cleaning Bin #1', capacity=100.0, cleaning_type='24_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #1', capacity=100.0, cleaning_type='12_hour'),
                    CleaningBin(name='24-Hour Cleaning Bin #2', capacity=150.0, cleaning_type='24_hour'),
                    CleaningBin(name='12-Hour Cleaning Bin #2', capacity=120.0, cleaning_type='12_hour')
                ]
                for cb in cleaning_bins:
                    db.session.add(cb)
                db.session.commit()
                print("Basic cleaning bins added!")
                
            # Add storage areas if they don't exist
            if not StorageArea.query.first():
                print("Adding basic storage areas...")
                storage_areas = [
                    StorageArea(name='Storage Area A', capacity_kg=10000.0, location='Ground Floor'),
                    StorageArea(name='Storage Area B', capacity_kg=15000.0, location='Ground Floor'),
                    StorageArea(name='Storage Area C', capacity_kg=12000.0, location='First Floor'),
                    StorageArea(name='Storage Area D', capacity_kg=8000.0, location='First Floor')
                ]
                for sa in storage_areas:
                    db.session.add(sa)
                db.session.commit()
                print("Basic storage areas added!")
                
            # Add B1 scale cleaning machine if it doesn't exist
            if not B1ScaleCleaning.query.first():
                print("Adding B1 Scale cleaning machine...")
                from datetime import datetime, timedelta
                b1_machine = B1ScaleCleaning(
                    machine_name='B1 Scale',
                    cleaning_frequency_minutes=60,
                    last_cleaned=datetime.utcnow(),
                    next_cleaning_due=datetime.utcnow() + timedelta(minutes=60),
                    status='due'
                )
                db.session.add(b1_machine)
                db.session.commit()
                print("B1 Scale machine added!")
                
    except Exception as e:
        print(f"Error initializing tables: {e}")
        db.session.rollback()

if __name__ == "__main__":
    init_missing_tables()
