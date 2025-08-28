
import os
import sqlite3
from sqlalchemy import create_engine, text

def migrate_cleaning_process():
    """Add missing fields to cleaning_process table"""
    
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
        ('is_locked', 'BOOLEAN', 'DEFAULT TRUE'),
        ('reminder_sent_5min', 'BOOLEAN', 'DEFAULT FALSE'),
        ('reminder_sent_10min', 'BOOLEAN', 'DEFAULT FALSE'),
        ('reminder_sent_30min', 'BOOLEAN', 'DEFAULT FALSE'),
        ('next_process_job_id', 'INTEGER')
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
                        WHERE table_name = 'cleaning_process'
                    """))
                    existing_columns = [row[0] for row in result]
                else:
                    # SQLite syntax
                    result = conn.execute(text("PRAGMA table_info(cleaning_process)"))
                    existing_columns = [row[1] for row in result]
                
                print(f"Existing columns in cleaning_process: {existing_columns}")
                
                # Add missing columns
                for column_name, column_type, default_value in new_columns:
                    if column_name not in existing_columns:
                        try:
                            if 'postgresql' in str(engine.url):
                                # PostgreSQL syntax
                                if column_type == 'BOOLEAN':
                                    sql = f"ALTER TABLE cleaning_process ADD COLUMN {column_name} BOOLEAN {default_value}"
                                elif column_type == 'INTEGER':
                                    sql = f"ALTER TABLE cleaning_process ADD COLUMN {column_name} INTEGER"
                                else:
                                    sql = f"ALTER TABLE cleaning_process ADD COLUMN {column_name} {column_type}"
                            else:
                                # SQLite syntax
                                if default_value:
                                    sql = f"ALTER TABLE cleaning_process ADD COLUMN {column_name} {column_type} {default_value}"
                                else:
                                    sql = f"ALTER TABLE cleaning_process ADD COLUMN {column_name} {column_type}"
                            
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
                
                # Add foreign key constraint for next_process_job_id if it doesn't exist
                if 'next_process_job_id' not in existing_columns:
                    try:
                        if 'postgresql' in str(engine.url):
                            conn.execute(text("""
                                ALTER TABLE cleaning_process 
                                ADD CONSTRAINT fk_cleaning_process_next_job 
                                FOREIGN KEY (next_process_job_id) 
                                REFERENCES production_job_new(id)
                            """))
                            conn.commit()
                            print("Added foreign key constraint for next_process_job_id")
                    except Exception as e:
                        print(f"Note: Could not add foreign key constraint: {e}")
                
                print("Cleaning process table migration completed successfully!")
                
            except Exception as e:
                print(f"Error checking table structure: {e}")
                
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_cleaning_process()
