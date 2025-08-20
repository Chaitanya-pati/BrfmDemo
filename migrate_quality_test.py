
#!/usr/bin/env python3
"""
Migration script to add sample photo columns to QualityTest table
"""

import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'wheat_processing.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the application first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(quality_test)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add sample_photos_before column if it doesn't exist
        if 'sample_photos_before' not in columns:
            cursor.execute("ALTER TABLE quality_test ADD COLUMN sample_photos_before VARCHAR(200)")
            print("Added sample_photos_before column")
        
        # Add sample_photos_after column if it doesn't exist
        if 'sample_photos_after' not in columns:
            cursor.execute("ALTER TABLE quality_test ADD COLUMN sample_photos_after VARCHAR(200)")
            print("Added sample_photos_after column")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
