import random
import string
from datetime import datetime
import csv

def generate_test_code(prefix='FZK', length=3):
    code = prefix + ''.join(random.choices(string.digits, k=length))
    return code

def format_datetime(dt=None):
    if not dt:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M')

def results_to_excel(results, filename='results.csv'):
    """CSV formatda natijalarni saqlash"""
    if not results:
        return filename
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    return filename 