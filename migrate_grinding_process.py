
import os
import psycopg2
from urllib.parse import urlparse

def migrate_grinding_process():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    print(f"Using database: {database_url}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'grinding_process'
            ORDER BY column_name;
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns in grinding_process: {existing_columns}")
        
        # Add missing columns for enhanced grinding process tracking
        columns_to_add = [
            ('b1_scale_operator', 'VARCHAR(100)'),
            ('b1_scale_start_time', 'TIMESTAMP'),
            ('b1_scale_weight_kg', 'FLOAT'),
            ('bran_percentage_alert', 'BOOLEAN DEFAULT FALSE'),
            ('main_products_percentage', 'FLOAT')
        ]
        
        for column_name, column_type in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE grinding_process ADD COLUMN {column_name} {column_type};")
                    print(f"Added column {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
            else:
                print(f"Column {column_name} already exists")
        
        # Commit all changes
        conn.commit()
        
        # Verify final columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'grinding_process'
            ORDER BY column_name;
        """)
        final_columns = [row[0] for row in cursor.fetchall()]
        print(f"Final columns in grinding_process: {final_columns}")
        
        cursor.close()
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_grinding_process()
