from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_no = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    full_name = models.CharField(max_length=100)
    collection_center = models.CharField(max_length=50, default='Main Center')

    def __str__(self):
        return f"{self.full_name} ({self.member_no})"

class Delivery(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    grade = models.CharField(max_length=20, choices=[
        ('A', 'Grade A'),
        ('B', 'Grade B'),
        ('C', 'Grade C'),
    ])
    center = models.CharField(max_length=50)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)

    def total_amount(self):
        return self.quantity * self.price_per_unit

    def __str__(self):
        return f"{self.farmer.full_name} - {self.date}"

class Payment(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ], default='pending')

    def __str__(self):
        return f"{self.farmer.full_name} - {self.amount} - {self.status}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class CoffeeBatch(models.Model):
    """Track coffee batches from delivery to processing"""
    STATUS_CHOICES = [
        ('in_store', 'In Store'),
        ('on_machine', 'On Machine'),
        ('processed', 'Processed'),
        ('sold', 'Sold'),
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, null=True, blank=True)
    batch_number = models.CharField(max_length=50, unique=True)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    grade = models.CharField(max_length=20, choices=[
        ('A', 'Grade A - Premium'),
        ('B', 'Grade B - Standard'),
        ('C', 'Grade C - Lower'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_store')
    location = models.CharField(max_length=100, default='Main Store')
    entry_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    sold_date = models.DateTimeField(null=True, blank=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Batch {self.batch_number} - {self.farmer.full_name} ({self.quantity_kg}kg)"

class CoffeeProcessingRecord(models.Model):
    """Track when coffee goes to the machine"""
    PROCESS_TYPE_CHOICES = [
        ('pulping', 'Pulping'),
        ('fermenting', 'Fermenting'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('hulling', 'Hulling'),
        ('grading', 'Grading'),
    ]
    
    coffee_batch = models.ForeignKey(CoffeeBatch, on_delete=models.CASCADE)
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPE_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    quantity_before = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_after = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loss_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.coffee_batch.batch_number} - {self.process_type}"

class CoffeeSale(models.Model):
    """Track coffee sales"""
    coffee_batch = models.ForeignKey(CoffeeBatch, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=200)
    buyer_contact = models.CharField(max_length=50)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ], default='pending')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Sale to {self.buyer_name} - {self.quantity_sold}kg"
