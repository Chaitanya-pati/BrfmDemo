
#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def migrate_manual_cleaning():
    """Add ManualCleaningLog table to database"""
    try:
        conn = sqlite3.connect('instance/wheat_processing.db')
        cursor = conn.cursor()
        
        # Create ManualCleaningLog table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manual_cleaning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                cleaning_process_id INTEGER,
                machine_name VARCHAR(100) NOT NULL DEFAULT 'Manual Cleaning Machine',
                operator_name VARCHAR(100) NOT NULL,
                cleaning_start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                cleaning_end_time DATETIME,
                duration_minutes FLOAT,
                before_photo VARCHAR(255),
                after_photo VARCHAR(255),
                notes TEXT,
                status VARCHAR(20) DEFAULT 'completed',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES production_order (id),
                FOREIGN KEY (cleaning_process_id) REFERENCES cleaning_process (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manual_cleaning_order_id ON manual_cleaning_log(order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manual_cleaning_process_id ON manual_cleaning_log(cleaning_process_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_manual_cleaning_start_time ON manual_cleaning_log(cleaning_start_time)')
        
        conn.commit()
        print("✅ ManualCleaningLog table created successfully!")
        
        # Verify table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manual_cleaning_log'")
        if cursor.fetchone():
            print("✅ Table verification successful!")
        else:
            print("❌ Table verification failed!")
            
    except Exception as e:
        print(f"❌ Error creating ManualCleaningLog table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_manual_cleaning()
