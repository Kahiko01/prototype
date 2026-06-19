import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karuhiu_site.settings')
django.setup()

from django.contrib.auth.models import User
from farmers.models import Farmer, Delivery, Payment, CoffeeBatch, Announcement
from datetime import datetime, timedelta
import random
import string

# Kenyan names - First names
FIRST_NAMES = [
    'James', 'Mary', 'John', 'Grace', 'Peter', 'Jane', 'David', 'Sarah', 
    'Michael', 'Agnes', 'Joseph', 'Margaret', 'Stephen', 'Esther', 'Patrick',
    'Pauline', 'Bernard', 'Catherine', 'Francis', 'Teresa', 'Anthony', 'Veronica',
    'Charles', 'Rebecca', 'Samuel', 'Dorothy', 'Thomas', 'Hellen', 'Robert', 'Joyce',
    'Daniel', 'Monica', 'George', 'Ann', 'Timothy', 'Martha', 'Nicholas', 'Judith',
    'Alex', 'Florence', 'Kevin', 'Beatrice', 'Mark', 'Alice', 'Simon', 'Nancy',
    'Luke', 'Doris', 'Felix', 'Jemima'
]

# Kenyan last names
LAST_NAMES = [
    'Mwangi', 'Ochieng', 'Otieno', 'Kiprop', 'Kariuki', 'Wanjiru', 'Njoroge', 'Omondi',
    'Ouma', 'Kemboi', 'Njeri', 'Njuguna', 'Waweru', 'Okoth', 'Muthoni', 'Kinyua',
    'Kamau', 'Achieng', 'Kiplagat', 'Wambui', 'Kibe', 'Akinyi', 'Maina', 'Atieno',
    'Chepkirui', 'Rono', 'Kipchumba', 'Nyambura', 'Kosgei', 'Korir', 'Wairimu', 'Kipkorir',
    'Chepkorir', 'Kipchoge', 'Chepngetich', 'Kibet', 'Chelangat', 'Kiptoo', 'Chebet', 'Kiprono'
]

# Kenyan phone prefixes
PHONE_PREFIXES = ['0710', '0711', '0712', '0713', '0714', '0715', '0716', '0717', '0718', '0719',
                  '0720', '0721', '0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729',
                  '0730', '0731', '0732', '0733', '0734', '0735', '0736', '0737', '0738', '0739',
                  '0740', '0741', '0742', '0743', '0744', '0745', '0746', '0747', '0748', '0749',
                  '0750', '0751', '0752', '0753', '0754', '0755', '0756', '0757', '0758', '0759']

# Collection centers
CENTERS = ['Nairobi Center', 'Kiambu Center', 'Thika Center', 'Nakuru Center', 
           'Eldoret Center', 'Kisumu Center', 'Meru Center', 'Nyeri Center',
           'Mombasa Center', 'Machakos Center']

# Coffee grades
GRADES = ['A', 'B', 'C']

# Statuses
STATUSES = ['in_store', 'on_machine', 'processed', 'sold']

def generate_phone():
    return random.choice(PHONE_PREFIXES) + ''.join(random.choices(string.digits, k=7))

def generate_member_no():
    return 'KAR' + ''.join(random.choices(string.digits, k=4))

def create_farmer(index):
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"
    
    # Create user
    username = f"farmer{index}"
    password = "farmer123"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f"{username}@karuhiu.co.ke"}
    )
    if created:
        user.set_password(password)
        user.save()
    
    # Create farmer
    farmer, created = Farmer.objects.get_or_create(
        user=user,
        defaults={
            'member_no': generate_member_no(),
            'full_name': full_name,
            'phone': generate_phone(),
            'collection_center': random.choice(CENTERS)
        }
    )
    
    if not created:
        # Update existing farmer
        farmer.full_name = full_name
        farmer.phone = generate_phone()
        farmer.collection_center = random.choice(CENTERS)
        farmer.save()
    
    return farmer

def generate_deliveries(farmer, count=10):
    deliveries = []
    today = datetime.now().date()
    
    for i in range(count):
        date = today - timedelta(days=random.randint(1, 90))
        quantity = round(random.uniform(50, 500), 2)
        grade = random.choice(GRADES)
        center = random.choice(CENTERS)
        price = random.choice([45, 50, 55, 60])
        
        delivery = Delivery.objects.create(
            farmer=farmer,
            date=date,
            quantity=quantity,
            grade=grade,
            center=center,
            price_per_unit=price
        )
        deliveries.append(delivery)
    
    return deliveries

def generate_payments(farmer, count=5):
    payments = []
    today = datetime.now().date()
    
    for i in range(count):
        date = today - timedelta(days=random.randint(5, 60))
        amount = random.randint(5000, 30000)
        deduction = random.randint(100, 1500)
        net = amount - deduction
        status = random.choice(['paid', 'pending'])
        
        payment = Payment.objects.create(
            farmer=farmer,
            amount=amount,
            deductions=deduction,
            net_amount=net,
            payment_date=date,
            status=status
        )
        payments.append(payment)
    
    return payments

def generate_coffee_batches(farmer, count=8):
    batches = []
    today = datetime.now()
    
    for i in range(count):
        status = random.choice(STATUSES)
        batch = CoffeeBatch.objects.create(
            farmer=farmer,
            batch_number=f"COF-{today.strftime('%Y%m%d')}-{CoffeeBatch.objects.count() + 1:03d}",
            quantity_kg=round(random.uniform(100, 800), 2),
            grade=random.choice(GRADES),
            status=status,
            location=random.choice(CENTERS),
            price_per_kg=random.choice([45, 50, 55, 60]),
            notes=f"Batch from {farmer.full_name}",
            entry_date=today - timedelta(days=random.randint(1, 30))
        )
        
        if status == 'processed':
            batch.processed_date = today - timedelta(days=random.randint(1, 15))
            batch.save()
        elif status == 'sold':
            batch.processed_date = today - timedelta(days=random.randint(10, 20))
            batch.sold_date = today - timedelta(days=random.randint(1, 10))
            batch.save()
        elif status == 'on_machine':
            batch.processed_date = today - timedelta(days=random.randint(1, 5))
            batch.save()
        
        batches.append(batch)
    
    return batches

def main():
    print("🌾 Generating 50 Farmers with Coffee Data...")
    print("=" * 50)
    
    # Clear existing data (optional - comment out if you want to keep)
    # Comment these out if you want to keep existing data
    # Farmer.objects.all().delete()
    # CoffeeBatch.objects.all().delete()
    # Delivery.objects.all().delete()
    # Payment.objects.all().delete()
    
    for i in range(1, 51):
        print(f"Creating farmer {i}/50...")
        farmer = create_farmer(i)
        
        # Generate 8-15 deliveries
        delivery_count = random.randint(8, 15)
        generate_deliveries(farmer, delivery_count)
        
        # Generate 4-8 payments
        payment_count = random.randint(4, 8)
        generate_payments(farmer, payment_count)
        
        # Generate 6-12 coffee batches
        batch_count = random.randint(6, 12)
        generate_coffee_batches(farmer, batch_count)
    
    # Create an announcement
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        Announcement.objects.get_or_create(
            title='Welcome to Karuhiu Utheri Digital Farmers!',
            defaults={
                'content': 'We are now serving 50+ farmers with real-time yield tracking, payment management, and coffee processing. Welcome to the future of farming! 🌱☕',
                'created_by': admin_user
            }
        )
    
    print("=" * 50)
    print("✅ Successfully generated:")
    print(f"   - {Farmer.objects.count()} farmers")
    print(f"   - {Delivery.objects.count()} deliveries")
    print(f"   - {Payment.objects.count()} payments")
    print(f"   - {CoffeeBatch.objects.count()} coffee batches")
    print("=" * 50)
    
    # Show sample farmers
    print("\n📋 Sample farmers:")
    for farmer in Farmer.objects.all()[:5]:
        print(f"   • {farmer.full_name} (Member: {farmer.member_no}) - {farmer.collection_center}")

if __name__ == "__main__":
    main()
