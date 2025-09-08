
#!/usr/bin/env python3
"""
Migration script to add order_id column to cleaning_process table
"""

import sqlite3
import os
from app import app

def migrate_cleaning_process_order_id():
    """Add order_id column to cleaning_process table if it doesn't exist"""
    
    db_path = os.path.join('instance', 'wheat_processing.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if order_id column exists
        cursor.execute("PRAGMA table_info(cleaning_process)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'order_id' not in columns:
            print("Adding order_id column to cleaning_process table...")
            
            # Add the order_id column
            cursor.execute("""
                ALTER TABLE cleaning_process 
                ADD COLUMN order_id INTEGER REFERENCES production_order(id)
            """)
            
            print("✓ order_id column added successfully!")
        else:
            print("✓ order_id column already exists in cleaning_process table")
        
        # Check if moisture fields exist and add them if missing
        if 'moisture_before' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN moisture_before REAL")
            print("✓ Added moisture_before column")
            
        if 'moisture_after' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN moisture_after REAL")
            print("✓ Added moisture_after column")
            
        if 'waste_material_kg' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN waste_material_kg REAL")
            print("✓ Added waste_material_kg column")
            
        if 'water_used_liters' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN water_used_liters REAL")
            print("✓ Added water_used_liters column")
            
        if 'machine_efficiency' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN machine_efficiency REAL")
            print("✓ Added machine_efficiency column")
            
        if 'post_process_notes' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN post_process_notes TEXT")
            print("✓ Added post_process_notes column")
            
        if 'completed_by' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN completed_by TEXT")
            print("✓ Added completed_by column")
            
        if 'completion_time' not in columns:
            cursor.execute("ALTER TABLE cleaning_process ADD COLUMN completion_time DATETIME")
            print("✓ Added completion_time column")
        
        conn.commit()
        conn.close()
        
        print("✅ Cleaning process table migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    with app.app_context():
        migrate_cleaning_process_order_id()
