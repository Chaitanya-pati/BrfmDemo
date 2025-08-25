
#!/usr/bin/env python3
"""
Migration script to add finished_good_type column to production_order table
"""

import os
import sqlite3
from sqlalchemy import create_engine, text

def migrate_database():
    """Add finished_good_type field to production_order table"""
    
    # Try to get database URL from environment or use SQLite
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Use SQLite
        db_path = os.path.join('instance', 'wheat_processing.db')
        if not os.path.exists(db_path):
            print("Database file not found!")
            return
        database_url = f'sqlite:///{db_path}'
    
    print(f"Using database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if table exists and get column info
            try:
                if 'postgresql' in str(engine.url):
                    # PostgreSQL syntax
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'production_order'
                    """))
                    existing_columns = [row[0] for row in result]
                else:
                    # SQLite syntax
                    result = conn.execute(text("PRAGMA table_info(production_order)"))
                    existing_columns = [row[1] for row in result]
                
                print(f"Existing columns: {existing_columns}")
                
                # Add finished_good_type column if missing
                if 'finished_good_type' not in existing_columns:
                    try:
                        if 'postgresql' in str(engine.url):
                            sql = "ALTER TABLE production_order ADD COLUMN finished_good_type VARCHAR(100)"
                        else:
                            sql = "ALTER TABLE production_order ADD COLUMN finished_good_type VARCHAR(100)"
                        
                        conn.execute(text(sql))
                        conn.commit()
                        print("Added finished_good_type column")
                    except Exception as e:
                        if "already exists" in str(e) or "duplicate column" in str(e):
                            print("Column finished_good_type already exists")
                        else:
                            print(f"Error adding finished_good_type: {e}")
                else:
                    print("Column finished_good_type already exists")
                
                print("Database migration completed successfully!")
                
            except Exception as e:
                print(f"Error checking table structure: {e}")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()
