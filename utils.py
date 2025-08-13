import os
import random
import string
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_order_number(prefix='PO'):
    """Generate unique order number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

def generate_job_id():
    """Generate unique job ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"JOB{timestamp}{random_suffix}"

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
