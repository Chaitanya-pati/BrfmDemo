
#!/usr/bin/env python3

import sqlite3
import os

def migrate_grinding_session_nullable():
    """Make b1_scale_weight_kg column nullable in grinding_session table"""
    
    # Database path
    db_path = os.path.join('instance', 'wheat_processing.db')
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        print("Starting grinding_session nullable migration...")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Connected to SQLite database successfully")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(grinding_session)")
        columns = cursor.fetchall()
        print("Current grinding_session schema:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
        # Since SQLite doesn't support ALTER COLUMN directly, we need to recreate the table
        print("Creating new grinding_session table with nullable b1_scale_weight_kg...")
        
        # Create new table with corrected schema
        cursor.execute("""
        CREATE TABLE grinding_session_new (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            duration_seconds INTEGER,
            timer_active BOOLEAN DEFAULT 0,
            b1_scale_operator VARCHAR(100) NOT NULL,
            b1_scale_handoff_time DATETIME,
            b1_scale_weight_kg FLOAT,  -- Made nullable
            b1_scale_notes TEXT,
            grinding_machine_name VARCHAR(100),  -- Made nullable
            grinding_operator VARCHAR(100),      -- Made nullable
            total_input_kg FLOAT,               -- Made nullable
            total_output_kg FLOAT DEFAULT 0,
            main_products_kg FLOAT DEFAULT 0,
            bran_kg FLOAT DEFAULT 0,
            main_products_percentage FLOAT DEFAULT 0,
            bran_percentage FLOAT DEFAULT 0,
            bran_alert_triggered BOOLEAN DEFAULT 0,
            status VARCHAR(20) DEFAULT 'preparing',
            created_at DATETIME,
            FOREIGN KEY (order_id) REFERENCES production_order (id)
        )
        """)
        
        # Copy existing data if any
        cursor.execute("SELECT COUNT(*) FROM grinding_session")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Copying {count} existing records...")
            cursor.execute("""
            INSERT INTO grinding_session_new 
            SELECT * FROM grinding_session
            """)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE grinding_session")
        cursor.execute("ALTER TABLE grinding_session_new RENAME TO grinding_session")
        
        # Commit changes
        conn.commit()
        
        # Verify the change
        cursor.execute("PRAGMA table_info(grinding_session)")
        columns = cursor.fetchall()
        print("✓ Updated grinding_session schema:")
        for col in columns:
            if col[1] == 'b1_scale_weight_kg':
                nullable_status = 'NULL' if not col[3] else 'NOT NULL'
                print(f"  ✓ {col[1]} {col[2]} {nullable_status}")
        
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
    migrate_grinding_session_nullable()
