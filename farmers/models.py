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
