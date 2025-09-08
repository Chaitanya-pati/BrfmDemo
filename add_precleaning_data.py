
import os
from app import app, db
from models import PrecleaningBin

def add_precleaning_data():
    """Add sample data to pre-cleaning bins"""
    with app.app_context():
        try:
            # Check if pre-cleaning bins already exist
            existing_bins = PrecleaningBin.query.all()
            
            if not existing_bins:
                print("Creating new pre-cleaning bins...")
                precleaning_bins = [
                    PrecleaningBin(name='Pre-cleaning Bin A1', capacity=150.0, current_stock=120.5),
                    PrecleaningBin(name='Pre-cleaning Bin A2', capacity=200.0, current_stock=180.3),
                    PrecleaningBin(name='Pre-cleaning Bin B1', capacity=175.0, current_stock=95.7),
                    PrecleaningBin(name='Pre-cleaning Bin B2', capacity=180.0, current_stock=160.2),
                    PrecleaningBin(name='Pre-cleaning Bin C1', capacity=220.0, current_stock=200.8),
                    PrecleaningBin(name='Pre-cleaning Bin C2', capacity=190.0, current_stock=75.4)
                ]
                
                for bin in precleaning_bins:
                    db.session.add(bin)
                
                db.session.commit()
                print("✓ Pre-cleaning bins created successfully!")
                
            else:
                print("Updating existing pre-cleaning bins with sample stock...")
                stock_updates = [120.5, 180.3, 95.7, 160.2, 200.8, 75.4]
                
                for i, bin in enumerate(existing_bins[:6]):  # Update first 6 bins
                    if i < len(stock_updates):
                        bin.current_stock = stock_updates[i]
                        print(f"Updated {bin.name}: {stock_updates[i]} tons")
                
                # Add more bins if needed
                if len(existing_bins) < 6:
                    additional_bins = [
                        PrecleaningBin(name=f'Pre-cleaning Bin {chr(65 + len(existing_bins) // 2)}{(len(existing_bins) % 2) + 1}', 
                                     capacity=180.0, current_stock=100.0)
                        for _ in range(6 - len(existing_bins))
                    ]
                    
                    for bin in additional_bins:
                        db.session.add(bin)
                        print(f"Added new bin: {bin.name}")
                
                db.session.commit()
                print("✓ Pre-cleaning bins updated successfully!")
            
            # Display current status
            print("\nCurrent Pre-cleaning Bins Status:")
            bins = PrecleaningBin.query.all()
            for bin in bins:
                utilization = (bin.current_stock / bin.capacity * 100) if bin.capacity > 0 else 0
                print(f"- {bin.name}: {bin.current_stock:.1f}/{bin.capacity:.1f} tons ({utilization:.1f}% full)")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding pre-cleaning data: {str(e)}")

if __name__ == '__main__':
    add_precleaning_data()
