
#!/usr/bin/env python3
"""
Migration script to add order_id column to cleaning_process table for PostgreSQL
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate_cleaning_process_postgresql():
    """Add order_id column to cleaning_process table if it doesn't exist"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("Connected to PostgreSQL database successfully")
        
        # Check if order_id column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process' 
            AND column_name = 'order_id'
        """)
        
        result = cur.fetchone()
        
        if result:
            print("✓ order_id column already exists")
            return True
        
        print("Adding order_id column to cleaning_process table...")
        
        # Add the order_id column with foreign key constraint
        cur.execute("""
            ALTER TABLE cleaning_process 
            ADD COLUMN order_id INTEGER REFERENCES production_order(id)
        """)
        
        print("✓ order_id column added successfully!")
        
        # Check if other columns exist and add them if missing
        columns_to_check = [
            ('actual_end_time', 'TIMESTAMP'),
            ('start_moisture', 'DOUBLE PRECISION'),
            ('end_moisture', 'DOUBLE PRECISION'), 
            ('target_moisture', 'DOUBLE PRECISION'),
            ('water_added_liters', 'DOUBLE PRECISION DEFAULT 0.0'),
            ('waste_collected_kg', 'DOUBLE PRECISION DEFAULT 0.0'),
            ('machine_name', 'VARCHAR(100)'),
            ('operator_name', 'VARCHAR(100)'),
            ('is_locked', 'BOOLEAN DEFAULT TRUE'),
            ('reminder_sent_5min', 'BOOLEAN DEFAULT FALSE'),
            ('reminder_sent_10min', 'BOOLEAN DEFAULT FALSE'),
            ('reminder_sent_30min', 'BOOLEAN DEFAULT FALSE')
        ]
        
        # Get all existing columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process'
        """)
        existing_columns = {row[0] for row in cur.fetchall()}
        
        # Add missing columns
        for column_name, column_type in columns_to_check:
            if column_name not in existing_columns:
                try:
                    cur.execute(f"""
                        ALTER TABLE cleaning_process 
                        ADD COLUMN {column_name} {column_type}
                    """)
                    print(f"✓ Added {column_name} column")
                except Exception as e:
                    print(f"⚠ Error adding {column_name} column: {e}")
            else:
                print(f"✓ {column_name} column already exists")
        
        print("Migration completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Starting PostgreSQL cleaning_process migration...")
    success = migrate_cleaning_process_postgresql()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
