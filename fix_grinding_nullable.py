
#!/usr/bin/env python3

import psycopg2
import os
from urllib.parse import urlparse

def migrate_grinding_nullable():
    """Make b1_scale_weight_kg and other fields nullable in grinding_session table"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment!")
        return False
    
    try:
        print("Starting grinding_session nullable migration...")
        
        # Parse database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database successfully")
        
        # Make the problematic columns nullable
        nullable_columns = [
            'b1_scale_weight_kg',
            'grinding_machine_name', 
            'grinding_operator',
            'total_input_kg'
        ]
        
        for column in nullable_columns:
            try:
                cursor.execute(f"""
                ALTER TABLE grinding_session 
                ALTER COLUMN {column} DROP NOT NULL
                """)
                print(f"✓ Made {column} nullable")
            except Exception as e:
                print(f"⚠️  Column {column} might already be nullable: {e}")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    migrate_grinding_nullable()
