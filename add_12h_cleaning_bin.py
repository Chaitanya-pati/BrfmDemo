
#!/usr/bin/env python3
"""
Script to add 12-hour cleaning bin to the database
"""
from app import app, db
from models import CleaningBin

def add_12h_cleaning_bin():
    with app.app_context():
        # Check if 12-hour cleaning bin already exists
        existing_bin = CleaningBin.query.filter_by(name='12-Hour Cleaning Bin #1').first()
        if existing_bin:
            print("12-hour cleaning bin already exists")
            return

        # Create 12-hour cleaning bin
        bin_12h = CleaningBin(
            name='12-Hour Cleaning Bin #1',
            capacity=5000.0,  # 5 tons capacity
            current_stock=0.0,
            status='available',
            location='12-Hour Cleaning Area',
            cleaning_type='12_hour'
        )

        db.session.add(bin_12h)
        db.session.commit()
        print("12-hour cleaning bin created successfully!")

if __name__ == '__main__':
    add_12h_cleaning_bin()
