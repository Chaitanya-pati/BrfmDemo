
from app import app, db
from models import *

def fix_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database tables recreated successfully!")
        
        # Add some basic data if needed
        try:
            from populate_dummy_data import populate_data
            populate_data()
            print("Sample data populated successfully!")
        except Exception as e:
            print(f"Note: Could not populate sample data: {e}")

if __name__ == '__main__':
    fix_database()
