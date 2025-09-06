
#!/usr/bin/env python3
"""
Migration script to fix product table schema
"""

import os
import sys
from sqlalchemy import create_engine, text

def migrate_product_table():
    """Add missing fields to product table"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return False
    
    print(f"Using database: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Check current table structure
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'product'
                """))
                existing_columns = [row[0] for row in result]
                print(f"Current product columns: {existing_columns}")
                
                # Add missing columns
                if 'unit' not in existing_columns:
                    conn.execute(text("ALTER TABLE product ADD COLUMN unit VARCHAR(20) DEFAULT 'kg'"))
                    print("✓ Added unit column")
                
                if 'standard_price' not in existing_columns:
                    conn.execute(text("ALTER TABLE product ADD COLUMN standard_price FLOAT DEFAULT 0.0"))
                    print("✓ Added standard_price column")
                
                trans.commit()
                print("✅ Product table migration completed!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Product migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_product_table()
    sys.exit(0 if success else 1)
