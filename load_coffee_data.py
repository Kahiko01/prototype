import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karuhiu_site.settings')
django.setup()

from django.contrib.auth.models import User
from farmers.models import Farmer, CoffeeBatch, CoffeeProcessingRecord
from datetime import datetime, timedelta
import random

# Get a farmer
farmer = Farmer.objects.first()

if farmer:
    # Create sample coffee batches
    statuses = ['in_store', 'on_machine', 'processed', 'sold']
    for i in range(10):
        CoffeeBatch.objects.create(
            farmer=farmer,
            batch_number=f"COF-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
            quantity_kg=random.randint(50, 500),
            grade=random.choice(['A', 'B', 'C']),
            status=random.choice(statuses),
            location=random.choice(['Main Store', 'Kiambu Store', 'Thika Store']),
            price_per_kg=random.choice([45, 50, 55, 60]),
            notes=f"Sample batch {i+1}"
        )
    
    print("✅ Sample coffee data loaded successfully!")
else:
    print("❌ No farmers found. Run load_data.py first.")
