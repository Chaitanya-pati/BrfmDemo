
#!/usr/bin/env python3
"""
Migration script to fix production_order table schema
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.exc import SQLAlchemyError

def migrate_production_order():
    """Fix production_order table schema"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return False
    
    print(f"Using database: {database_url}")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check current table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'production_order'
                    ORDER BY column_name;
                """))
                existing_columns = {row[0]: {'type': row[1], 'nullable': row[2]} for row in result}
                print(f"Current columns: {list(existing_columns.keys())}")
                
                # Drop constraints first if they exist
                try:
                    conn.execute(text("ALTER TABLE production_order DROP CONSTRAINT IF EXISTS production_order_customer_id_fkey"))
                    conn.execute(text("ALTER TABLE production_order DROP CONSTRAINT IF EXISTS production_order_product_id_fkey"))
                    print("Dropped existing foreign key constraints")
                except Exception as e:
                    print(f"Note: {e}")
                
                # Handle customer field
                if 'customer' in existing_columns and 'customer_id' not in existing_columns:
                    print("Converting customer field to customer_id...")
                    # Add customer_id column
                    conn.execute(text("ALTER TABLE production_order ADD COLUMN customer_id INTEGER"))
                    
                    # Try to map existing customer names to IDs
                    conn.execute(text("""
                        UPDATE production_order 
                        SET customer_id = (
                            SELECT id FROM customer 
                            WHERE company_name = production_order.customer 
                            LIMIT 1
                        )
                        WHERE customer IS NOT NULL
                    """))
                    
                    # Drop old customer column
                    conn.execute(text("ALTER TABLE production_order DROP COLUMN customer"))
                    print("✓ Converted customer to customer_id")
                
                # Handle product field
                if 'product' in existing_columns and 'product_id' not in existing_columns:
                    print("Converting product field to product_id...")
                    # Add product_id column
                    conn.execute(text("ALTER TABLE production_order ADD COLUMN product_id INTEGER"))
                    
                    # Try to map existing product names to IDs
                    conn.execute(text("""
                        UPDATE production_order 
                        SET product_id = (
                            SELECT id FROM product 
                            WHERE name = production_order.product 
                            LIMIT 1
                        )
                        WHERE product IS NOT NULL
                    """))
                    
                    # Drop old product column
                    conn.execute(text("ALTER TABLE production_order DROP COLUMN product"))
                    print("✓ Converted product to product_id")
                
                # Add foreign key constraints
                try:
                    conn.execute(text("""
                        ALTER TABLE production_order 
                        ADD CONSTRAINT production_order_customer_id_fkey 
                        FOREIGN KEY (customer_id) REFERENCES customer(id)
                    """))
                    print("✓ Added customer_id foreign key")
                except Exception as e:
                    print(f"Note: Customer FK constraint: {e}")
                
                try:
                    conn.execute(text("""
                        ALTER TABLE production_order 
                        ADD CONSTRAINT production_order_product_id_fkey 
                        FOREIGN KEY (product_id) REFERENCES product(id)
                    """))
                    print("✓ Added product_id foreign key")
                except Exception as e:
                    print(f"Note: Product FK constraint: {e}")
                
                # Commit transaction
                trans.commit()
                print("✅ Production order schema migration completed successfully!")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_production_order()
    sys.exit(0 if success else 1)
