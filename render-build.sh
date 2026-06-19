#!/bin/bash
set -e

echo "===== Installing dependencies ====="
pip install -r requirements.txt

echo "===== Running migrations ====="
python manage.py migrate --noinput

echo "===== Collecting static files ====="
python manage.py collectstatic --noinput

echo "===== Creating superuser ====="
python -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@karuhiu.co.ke', 'board2026')"

echo "===== Loading sample data ====="
python load_data.py

echo "===== Generating farmers ====="
python generate_farmers.py

echo "===== Build complete! ====="
