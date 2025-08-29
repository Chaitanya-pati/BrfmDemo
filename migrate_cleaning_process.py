import os
import psycopg2
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection from environment variable"""
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('REPLIT_DB_URL')

    if not db_url:
        print("No database URL found in environment variables")
        return None

    try:
        # Parse the database URL
        parsed = urlparse(db_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def migrate_cleaning_process():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        print("Using database:", os.environ.get('DATABASE_URL') or os.environ.get('REPLIT_DB_URL'))

        # Get existing columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process' AND table_schema = 'public'
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        print("Existing columns in cleaning_process:", existing_columns)

        # Add missing columns one by one
        columns_to_add = [
            ('next_process_job_id', 'INTEGER REFERENCES production_job_new(id)'),
            ('is_locked', 'BOOLEAN DEFAULT TRUE'),
            ('reminder_sent_5min', 'BOOLEAN DEFAULT FALSE'),
            ('reminder_sent_10min', 'BOOLEAN DEFAULT FALSE'),
            ('reminder_sent_30min', 'BOOLEAN DEFAULT FALSE')
        ]

        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    cur.execute(f"ALTER TABLE cleaning_process ADD COLUMN {column_name} {column_def}")
                    conn.commit()
                    print(f"Added column {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
                    conn.rollback()
            else:
                print(f"Column {column_name} already exists")

        # Verify all columns were added
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cleaning_process' AND table_schema = 'public'
            ORDER BY column_name
        """)
        final_columns = [row[0] for row in cur.fetchall()]
        print("Final columns in cleaning_process:", final_columns)

        conn.close()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_cleaning_process()