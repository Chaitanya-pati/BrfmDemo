
#!/usr/bin/env python3

from app import app, db
from models import PrecleaningProcess
from datetime import datetime, timedelta

def cleanup_stuck_precleaning():
    """Clean up stuck precleaning processes"""
    with app.app_context():
        try:
            print("🔍 Checking for stuck precleaning processes...")
            
            # Consider processes stuck if running for more than 4 hours
            stuck_cutoff = datetime.utcnow() - timedelta(hours=4)
            
            # Find all running processes
            running_processes = PrecleaningProcess.query.filter_by(status='running').all()
            stuck_processes = []
            
            print(f"📊 Found {len(running_processes)} running precleaning processes")
            
            for process in running_processes:
                elapsed_hours = (datetime.utcnow() - process.start_time).total_seconds() / 3600
                print(f"   Process #{process.id}: Started {process.start_time}, Running for {elapsed_hours:.1f} hours")
                
                if process.start_time < stuck_cutoff:
                    stuck_processes.append(process)
            
            if stuck_processes:
                print(f"\n🚨 Found {len(stuck_processes)} stuck processes (running >4 hours)")
                
                for process in stuck_processes:
                    elapsed_hours = (datetime.utcnow() - process.start_time).total_seconds() / 3600
                    print(f"   Cleaning up Process #{process.id} (running for {elapsed_hours:.1f} hours)")
                    
                    process.status = 'completed'
                    process.timer_active = False
                    process.end_time = datetime.utcnow()
                    process.duration_seconds = int((process.end_time - process.start_time).total_seconds())
                
                db.session.commit()
                print(f"✅ Successfully cleaned up {len(stuck_processes)} stuck processes")
            else:
                print("✅ No stuck processes found")
            
            # Show current status
            current_running = PrecleaningProcess.query.filter_by(status='running').count()
            print(f"\n📈 Current status: {current_running} running precleaning processes")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during cleanup: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    print("🧹 Precleaning Process Cleanup Tool")
    print("=" * 50)
    
    if cleanup_stuck_precleaning():
        print("\n✅ Cleanup completed successfully!")
    else:
        print("\n❌ Cleanup failed!")
