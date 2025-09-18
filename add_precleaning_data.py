
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
                    PrecleaningBin(name='Pre-cleaning Bin A1', capacity=150.0, current_stock=135.5),
                    PrecleaningBin(name='Pre-cleaning Bin A2', capacity=200.0, current_stock=185.3),
                    PrecleaningBin(name='Pre-cleaning Bin B1', capacity=175.0, current_stock=145.7),
                    PrecleaningBin(name='Pre-cleaning Bin B2', capacity=180.0, current_stock=165.2),
                    PrecleaningBin(name='Pre-cleaning Bin C1', capacity=220.0, current_stock=205.8),
                    PrecleaningBin(name='Pre-cleaning Bin C2', capacity=190.0, current_stock=155.4),
                    PrecleaningBin(name='Pre-cleaning Bin D1', capacity=160.0, current_stock=125.0),
                    PrecleaningBin(name='Pre-cleaning Bin D2', capacity=170.0, current_stock=140.5),
                    PrecleaningBin(name='Pre-cleaning Bin E1', capacity=140.0, current_stock=115.3),
                    PrecleaningBin(name='Pre-cleaning Bin E2', capacity=165.0, current_stock=130.8)
                ]
                
                for bin in precleaning_bins:
                    db.session.add(bin)
                
                db.session.commit()
                print("✓ Pre-cleaning bins created successfully!")
                
            else:
                print("Updating existing pre-cleaning bins with sample stock...")
                stock_updates = [135.5, 185.3, 145.7, 165.2, 205.8, 155.4, 125.0, 140.5, 115.3, 130.8]
                
                for i, bin in enumerate(existing_bins[:10]):  # Update first 10 bins
                    if i < len(stock_updates):
                        bin.current_stock = stock_updates[i]
                        print(f"Updated {bin.name}: {stock_updates[i]} tons")
                
                # Add more bins if needed
                if len(existing_bins) < 10:
                    bin_names = ['D1', 'D2', 'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2']
                    additional_bins = []
                    for i in range(len(existing_bins), 10):
                        bin_name = f'Pre-cleaning Bin {bin_names[i - 6] if i >= 6 else bin_names[i]}'
                        capacity = 160.0 + (i * 5)  # Varying capacity
                        stock = capacity * 0.75  # 75% filled
                        additional_bins.append(
                            PrecleaningBin(name=bin_name, capacity=capacity, current_stock=stock)
                        )
                    
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
