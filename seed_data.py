import os
import django
import random
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from doctors.models import Remake

def seed():
    Remake.objects.all().delete()
    print("Cleaned database...")

    depts = [
        'Milling', 'Data Entry', 'Printed Dentures', 'Crown & Bridge', 
        'Quality Control', 'Frameworks/Metal', 'Repairs', 'Implants',
        'Model Room', 'Setup', 'Waxup', 'Boilout/Process', 'Finishers',
        'Billing', 'Survey/Design'
    ]
    reasons = ['Margin not clear', 'Shade wrong', 'Tight fit', 'Contour', 'Fractured']
    doctors = ['Dr. Smith', 'Dr. Jones', 'Dr. Miller', 'Dr. Brown', 'Dr. Wilson', 'Dr. Davis']
    
    
    for i in range(300):
        # Generate random days
        random_days = random.randint(0, 365)
        # Calculate the date
        date = timezone.now() - timedelta(days=random_days)
        
        Remake.objects.create(
            month=date.strftime("%B %Y"), 
            case_number=f"CN-{random.randint(10000, 99999)}",
            doctor_name=random.choice(doctors),
            department=random.choice(depts),
            units=random.randint(1, 10),
            remake_reason=random.choice(reasons),
            remake_units=random.randint(1, 3),
            date_entered=date 
        )
        
    print(f"Successfully seeded 300 remakes across 12 months!")

if __name__ == '__main__':
    seed()