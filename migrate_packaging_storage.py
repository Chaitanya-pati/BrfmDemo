
from app import app, db
from sqlalchemy import text

def migrate_packaging_storage():
    """Add storage_area_id column to packaging_record table"""
    with app.app_context():
        try:
            # Check if the column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='packaging_record' AND column_name='storage_area_id'
            """))
            
            if not result.fetchone():
                print("Adding storage_area_id column to packaging_record table...")
                
                # Add the storage_area_id column
                db.session.execute(text("""
                    ALTER TABLE packaging_record 
                    ADD COLUMN storage_area_id INTEGER REFERENCES storage_area(id)
                """))
                
                db.session.commit()
                print("✓ storage_area_id column added successfully!")
            else:
                print("✓ storage_area_id column already exists")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_packaging_storage()
