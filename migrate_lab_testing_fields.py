
import os
import sqlite3
from sqlalchemy import create_engine, text

def migrate_database():
    """Add new fields to quality_test table"""
    
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
        with engine.connect() as conn:
            # Check if table exists and get column info
            try:
                if 'postgresql' in str(engine.url):
                    # PostgreSQL syntax
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'quality_test'
                    """))
                    existing_columns = [row[0] for row in result]
                else:
                    # SQLite syntax
                    result = conn.execute(text("PRAGMA table_info(quality_test)"))
                    existing_columns = [row[1] for row in result]
                
                print(f"Existing columns: {existing_columns}")
                
                # Add missing columns
                for column_name, column_type in new_columns:
                    if column_name not in existing_columns:
                        try:
                            if 'postgresql' in str(engine.url):
                                # PostgreSQL uses DOUBLE PRECISION instead of REAL
                                sql = f"ALTER TABLE quality_test ADD COLUMN {column_name} DOUBLE PRECISION"
                            else:
                                sql = f"ALTER TABLE quality_test ADD COLUMN {column_name} {column_type}"
                            
                            conn.execute(text(sql))
                            conn.commit()
                            print(f"Added {column_name} column")
                        except Exception as e:
                            if "already exists" in str(e) or "duplicate column" in str(e):
                                print(f"Column {column_name} already exists")
                            else:
                                print(f"Error adding {column_name}: {e}")
                    else:
                        print(f"Column {column_name} already exists")
                
                print("Database migration completed successfully!")
                
            except Exception as e:
                print(f"Error checking table structure: {e}")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_database()
