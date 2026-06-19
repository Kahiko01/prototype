import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karuhiu_site.settings')
django.setup()

from django.contrib.auth.models import User
from farmers.models import Farmer, Delivery, Payment, Announcement
from datetime import datetime, timedelta
import random

# Create admin user if not exists
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@karuhiu.co.ke'}
)
if created:
    admin.set_password('board2026')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

# Create a demo farmer
farmer_user, created = User.objects.get_or_create(
    username='farmer1',
    defaults={'email': 'farmer@karuhiu.co.ke'}
)
if created:
    farmer_user.set_password('farmer123')
    farmer_user.save()

farmer, created = Farmer.objects.get_or_create(
    user=farmer_user,
    defaults={
        'member_no': 'KAR001',
        'full_name': 'James Mwangi',
        'phone': '0712345678',
        'collection_center': 'Nairobi Center'
    }
)

# Create sample deliveries
today = datetime.now().date()
for i in range(10):
    date = today - timedelta(days=random.randint(1, 30))
    Delivery.objects.create(
        farmer=farmer,
        date=date,
        quantity=round(random.uniform(50, 500), 2),
        grade=random.choice(['A', 'B', 'C']),
        center=random.choice(['Nairobi Center', 'Kiambu Center', 'Thika Center']),
        price_per_unit=random.choice([45, 50, 55, 60])
    )

# Create sample payments
for i in range(3):
    date = today - timedelta(days=random.randint(5, 20))
    amount = random.randint(5000, 20000)
    deduction = random.randint(100, 1000)
    Payment.objects.create(
        farmer=farmer,
        amount=amount,
        deductions=deduction,
        net_amount=amount - deduction,
        payment_date=date,
        status=random.choice(['paid', 'pending'])
    )

# Create an announcement
Announcement.objects.get_or_create(
    title='New Collection Center Opening',
    defaults={
        'content': 'We are excited to announce a new collection center in Thika. Farmers in the area can now deliver their produce starting next week.',
        'created_by': admin
    }
)

print("✅ Sample data loaded successfully!")
print("👤 Admin login: admin / board2026")
print("👤 Farmer login: farmer1 / farmer123")
