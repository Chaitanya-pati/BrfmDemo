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


