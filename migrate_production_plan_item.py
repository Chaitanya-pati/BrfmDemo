
#!/usr/bin/env python3
"""
Migration script to add calculated_tons column to production_plan_item table
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate_production_plan_item():
    """Add calculated_tons column to production_plan_item table"""
    
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
        
        print("Connected to database successfully")
        
        # Check if calculated_tons column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'production_plan_item' 
            AND column_name = 'calculated_tons'
        """)
        
        result = cur.fetchone()
        
        if result:
            print("✓ calculated_tons column already exists")
            return True
        
        print("Adding calculated_tons column to production_plan_item table...")
        
        # Add the calculated_tons column
        cur.execute("""
            ALTER TABLE production_plan_item 
            ADD COLUMN calculated_tons DOUBLE PRECISION
        """)
        
        print("✓ calculated_tons column added successfully")
        
        # Update existing records to calculate the tons based on percentage
        print("Updating existing records with calculated tons...")
        
        cur.execute("""
            UPDATE production_plan_item 
            SET calculated_tons = (
                SELECT (ppi.percentage / 100.0) * po.quantity 
                FROM production_plan pp 
                JOIN production_order po ON pp.order_id = po.id 
                WHERE pp.id = production_plan_item.plan_id
            )
            WHERE calculated_tons IS NULL
        """)
        
        rows_updated = cur.rowcount
        print(f"✓ Updated {rows_updated} existing records with calculated tons")
        
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
    print("Starting production_plan_item migration...")
    success = migrate_production_plan_item()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
#!/usr/bin/env python3
"""
Migration script to add calculated_tons column to production_plan_item table
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def migrate_production_plan_item():
    """Add calculated_tons column to production_plan_item table"""
    
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
        
        print("Connected to database successfully")
        
        # Check if calculated_tons column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'production_plan_item' 
            AND column_name = 'calculated_tons'
        """)
        
        result = cur.fetchone()
        
        if result:
            print("✓ calculated_tons column already exists")
            return True
        
        print("Adding calculated_tons column to production_plan_item table...")
        
        # Add the calculated_tons column
        cur.execute("""
            ALTER TABLE production_plan_item 
            ADD COLUMN calculated_tons DOUBLE PRECISION
        """)
        
        print("✓ calculated_tons column added successfully")
        
        # Update existing records to calculate the tons based on percentage
        print("Updating existing records with calculated tons...")
        
        cur.execute("""
            UPDATE production_plan_item 
            SET calculated_tons = (
                SELECT (ppi.percentage / 100.0) * po.quantity 
                FROM production_plan pp 
                JOIN production_order po ON pp.order_id = po.id 
                WHERE pp.id = production_plan_item.plan_id
            )
            WHERE calculated_tons IS NULL
        """)
        
        rows_updated = cur.rowcount
        print(f"✓ Updated {rows_updated} existing records with calculated tons")
        
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
    print("Starting production_plan_item migration...")
    success = migrate_production_plan_item()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
