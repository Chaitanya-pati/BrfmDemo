
#!/usr/bin/env python3
"""
Migration script to make job_id column nullable in cleaning_process table
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_job_id_nullable():
    """Make job_id column nullable in cleaning_process table"""
    
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
        
        # Check current constraint on job_id column
        cur.execute("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process' 
            AND column_name = 'job_id'
        """)
        
        result = cur.fetchone()
        
        if result and result[0] == 'YES':
            print("✓ job_id column is already nullable")
            return True
        
        print("Making job_id column nullable...")
        
        # Make job_id column nullable
        cur.execute("""
            ALTER TABLE cleaning_process 
            ALTER COLUMN job_id DROP NOT NULL
        """)
        
        print("✓ job_id column is now nullable!")
        
        # Verify the change
        cur.execute("""
            SELECT is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process' 
            AND column_name = 'job_id'
        """)
        
        result = cur.fetchone()
        if result and result[0] == 'YES':
            print("✓ Verification successful: job_id column is nullable")
        else:
            print("⚠ Verification failed: job_id column may still have constraints")
        
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
    print("Starting job_id nullable migration...")
    success = fix_job_id_nullable()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
