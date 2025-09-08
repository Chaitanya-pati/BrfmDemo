import os
import random
import string
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_order_number(prefix='ORD'):
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}{random.randint(10, 99)}"

def generate_job_id():
    """Generate unique job ID for transfer jobs"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"TJ{timestamp}{random.randint(10, 99)}"

def calculate_production_percentages(plan_items, total_quantity):
    """Calculate quantities based on percentages"""
    results = []
    for item in plan_items:
        quantity = (item.percentage / 100) * total_quantity
        results.append({
            'bin_id': item.precleaning_bin_id,
            'percentage': item.percentage,
            'quantity': quantity
        })
    return results

def format_weight(weight_in_kg):
    """Format weight for display"""
    if weight_in_kg >= 1000:
        return f"{weight_in_kg / 1000:.2f} tons"
    else:
        return f"{weight_in_kg:.2f} kg"

def get_file_url(filename):
    """Get URL for uploaded file"""
    if filename:
        return f"/uploads/{filename}"
    return None

def notify_responsible_person(order_number, responsible_person, finished_goods_type, quantity_tons):
    """Notify responsible person about new production order"""
    # For now, we'll just log the notification
    # In a real system, this would send an email, SMS, or system notification
    import logging
    logging.info(f"NOTIFICATION: Order {order_number} created for {responsible_person}")
    logging.info(f"  - Type: {finished_goods_type}")
    logging.info(f"  - Quantity: {quantity_tons} tons")
    return True

def validate_plan_percentages(plan_items):
    """Validate that percentages sum to exactly 100%"""
    total = sum(item['percentage'] for item in plan_items)
    return abs(total - 100.0) < 0.001  # Allow for small floating point errors