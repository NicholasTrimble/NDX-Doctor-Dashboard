import os
import django
import random
from datetime import timedelta

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from doctors.models import Remake
from django.utils import timezone

def seed():
    print("Cleaning database...")
    Remake.objects.all().delete()

    # 2. Real Categories from your Excel Sheet
    depts = ['Fixed', 'Denture', 'Appliance', 'CT Guided']
    reasons = [
        'Contour', 'Implant Doctor', 'Fit Doctor', 'Margin Doctor', 
        'Margin Lab', 'Treatment Change', 'Shade Doctor', 'Broke/Fracture', 
        'Fit to Crown', 'Contact', 'Bite Doctor'
    ]
    doctors = [
        'Dr. Abraham Smith', 'Dr. Benjamin Jones', 'Dr. Catherine Miller', 
        'Dr. David Wilson', 'Dr. Elizabeth Brown', 'Dr. Frank Davis'
    ]

    print("Generating 1,000 realistic production records...")

    # 3. Generate Data
    for i in range(1000):
        # Pick a random date in the last 12 months
        random_days = random.randint(0, 365)
        date = timezone.now() - timedelta(days=random_days)
        
        doc = random.choice(doctors)
        dept = random.choice(depts)
        
        # Realistic Units for a dental case
        total_units = random.randint(1, 8)
        
        # LOGIC: Only some cases are remakes (approx 5% remake rate)
        is_remake = random.random() < 0.06 
        
        remake_u = 0
        adj_u = 0
        reason = ""
        
        if is_remake:
            # If it's a remake, assign remake units and a reason from the Excel list
            remake_u = random.randint(1, total_units)
            adj_u = random.choice([0, 1]) # Sometimes there's an adjustment unit
            reason = random.choice(reasons)
        
        Remake.objects.create(
            month=date.strftime("%Y%m"), # Matches your Excel '202503' style
            case_number=f"CN-{random.randint(100000, 999999)}",
            doctor_name=doc,
            department=dept,
            units=total_units,
            remake_units=remake_u,
            adjustment_units=adj_u,
            remake_reason=reason,
            date_entered=date
        )

    print("Successfully seeded 1,000 records!")
    print("Dashboard should now show realistic percentages (approx 3-8%).")

if __name__ == '__main__':
    seed()