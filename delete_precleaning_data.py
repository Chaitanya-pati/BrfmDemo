
#!/usr/bin/env python3

from app import app, db
from models import Transfer, PrecleaningProcess, ManualCleaningLog, PrecleaningReminder

def delete_precleaning_data():
    """Delete all precleaning transfer data and related records"""
    with app.app_context():
        try:
            print("🗑️ Starting deletion of precleaning transfer data...")
            
            # Count records before deletion
            transfer_count = Transfer.query.filter_by(transfer_type='godown_to_precleaning').count()
            process_count = PrecleaningProcess.query.count()
            manual_cleaning_count = ManualCleaningLog.query.filter(ManualCleaningLog.precleaning_process_id.isnot(None)).count()
            reminder_count = PrecleaningReminder.query.count()
            
            print(f"📊 Found records to delete:")
            print(f"   📋 Precleaning transfers: {transfer_count}")
            print(f"   ⚙️ Precleaning processes: {process_count}")
            print(f"   🧹 Manual cleaning logs: {manual_cleaning_count}")
            print(f"   ⏰ Precleaning reminders: {reminder_count}")
            
            # Delete in proper order to respect foreign key constraints
            
            # 1. Delete precleaning reminders first
            deleted_reminders = PrecleaningReminder.query.delete()
            print(f"✅ Deleted {deleted_reminders} precleaning reminders")
            
            # 2. Delete manual cleaning logs linked to precleaning processes
            deleted_manual_cleanings = ManualCleaningLog.query.filter(
                ManualCleaningLog.precleaning_process_id.isnot(None)
            ).delete(synchronize_session='fetch')
            print(f"✅ Deleted {deleted_manual_cleanings} manual cleaning logs")
            
            # 3. Delete precleaning processes
            deleted_processes = PrecleaningProcess.query.delete()
            print(f"✅ Deleted {deleted_processes} precleaning processes")
            
            # 4. Delete precleaning transfers
            deleted_transfers = Transfer.query.filter_by(transfer_type='godown_to_precleaning').delete()
            print(f"✅ Deleted {deleted_transfers} precleaning transfers")
            
            # Commit all changes
            db.session.commit()
            
            print("\n🎉 Successfully deleted all precleaning transfer data!")
            print("📝 Note: Godown and precleaning bin stock levels have NOT been adjusted.")
            print("   You may need to manually correct stock levels if needed.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting precleaning data: {str(e)}")
            return False
            
        return True

def reset_precleaning_bin_stocks():
    """Reset all precleaning bin stocks to zero"""
    try:
        from models import PrecleaningBin
        
        bins = PrecleaningBin.query.all()
        for bin in bins:
            old_stock = bin.current_stock
            bin.current_stock = 0.0
            print(f"   📦 {bin.name}: {old_stock} kg → 0 kg")
        
        db.session.commit()
        print("✅ Reset all precleaning bin stocks to zero")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resetting bin stocks: {str(e)}")

if __name__ == "__main__":
    print("🧹 Precleaning Data Deletion Tool")
    print("=" * 50)
    
    # Ask for confirmation
    confirm = input("\n⚠️  This will DELETE ALL precleaning transfer data. Are you sure? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = delete_precleaning_data()
        
        if success:
            reset_bins = input("\n📦 Do you want to reset all precleaning bin stocks to zero? (yes/no): ")
            if reset_bins.lower() == 'yes':
                reset_precleaning_bin_stocks()
        
        print("\n✅ Operation completed!")
    else:
        print("❌ Operation cancelled.")
