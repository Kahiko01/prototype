# Karuhiu Utheri Digital Farmers Cooperative

## 🌾 About
A digital platform for farmers to track produce deliveries, payments, and cooperative announcements.

## 🚀 Features
- Farmer Dashboard with yield charts
- Delivery and payment history
- PDF statement generation
- Staff delivery recording
- Announcements system
- Farmer search

## 🔐 Demo Credentials
- **Admin:** admin / board2026
- **Farmer:** farmer1 / farmer123

## 🛠️ Tech Stack
- Django 4.2
- SQLite
- ReportLab for PDFs
- Chart.js for visualizations

## 📦 Installation
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py load_data.py
python manage.py runserver
