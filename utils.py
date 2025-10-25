import random
import string
from datetime import datetime
import pandas as pd

def generate_test_code(prefix='FZK', length=3):
    code = prefix + ''.join(random.choices(string.digits, k=length))
    return code

def format_datetime(dt=None):
    if not dt:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M')

def results_to_excel(results, filename='results.xlsx'):
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)
    return filename 