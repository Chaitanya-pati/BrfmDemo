
import sqlite3
import os

def migrate_database():
    """Add new fields to quality_test table"""
    db_path = os.path.join('instance', 'wheat_processing.db')
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of new columns to add
    new_columns = [
        ('shrivelled_broken', 'REAL'),
        ('damaged', 'REAL'),
        ('weevilled', 'REAL'),
        ('other_food_grains', 'REAL'),
        ('sprouted', 'REAL'),
        ('immature', 'REAL'),
        ('test_weight', 'REAL'),
        ('gluten', 'REAL'),
        ('protein', 'REAL'),
        ('falling_number', 'REAL'),
        ('ash_content', 'REAL'),
        ('wet_gluten', 'REAL'),
        ('dry_gluten', 'REAL'),
        ('sedimentation_value', 'REAL')
    ]
    
    try:
        for column_name, column_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE quality_test ADD COLUMN {column_name} {column_type}")
                print(f"Added {column_name} column")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column {column_name} already exists")
                else:
                    print(f"Error adding {column_name}: {e}")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
