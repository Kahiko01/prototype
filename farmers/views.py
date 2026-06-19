from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from .models import Farmer, Delivery, Payment, Announcement
from datetime import datetime, timedelta
import json
import io

# Home page
def home(request):
    announcements = Announcement.objects.all().order_by('-date')[:3]
    return render(request, 'farmers/home.html', {'announcements': announcements})

# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'farmers/login.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Dashboard (protected)
@login_required
def dashboard(request):
    try:
        farmer = request.user.farmer
        # Get deliveries for this farmer
        deliveries = Delivery.objects.filter(farmer=farmer).order_by('-date')
        
        # Calculate totals
        total_quantity = deliveries.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_value = sum(d.total_amount() for d in deliveries)
        
        # Get payments
        payments = Payment.objects.filter(farmer=farmer).order_by('-payment_date')
        total_paid = payments.filter(status='paid').aggregate(Sum('net_amount'))['net_amount__sum'] or 0
        total_pending = payments.filter(status='pending').aggregate(Sum('net_amount'))['net_amount__sum'] or 0
        
        # Recent deliveries (last 5)
        recent_deliveries = deliveries[:5]
        
        context = {
            'farmer': farmer,
            'total_quantity': total_quantity,
            'total_value': total_value,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'recent_deliveries': recent_deliveries,
            'payments': payments[:5],
        }
        return render(request, 'farmers/dashboard.html', context)
    except Farmer.DoesNotExist:
        return render(request, 'farmers/dashboard.html', {'farmer': None})

@login_required
def yield_history(request):
    try:
        farmer = request.user.farmer
        deliveries = Delivery.objects.filter(farmer=farmer).order_by('-date')
        return render(request, 'farmers/yield_history.html', {'deliveries': deliveries})
    except Farmer.DoesNotExist:
        return redirect('dashboard')

@login_required
def payment_history(request):
    try:
        farmer = request.user.farmer
        payments = Payment.objects.filter(farmer=farmer).order_by('-payment_date')
        return render(request, 'farmers/payment_history.html', {'payments': payments})
    except Farmer.DoesNotExist:
        return redirect('dashboard')

@login_required
def announcements(request):
    announcements = Announcement.objects.all().order_by('-date')
    return render(request, 'farmers/announcements.html', {'announcements': announcements})

@login_required
def search_farmer(request):
    query = request.GET.get('q', '')
    farmers = None
    if query:
        farmers = Farmer.objects.filter(
            models.Q(member_no__icontains=query) | 
            models.Q(full_name__icontains=query)
        )
    return render(request, 'farmers/search_results.html', {'farmers': farmers, 'query': query})

@login_required
def staff_delivery(request):
    if not request.user.is_staff:
        messages.error(request, 'Staff access required')
        return redirect('dashboard')
    
    if request.method == 'POST':
        member_no = request.POST['member_no']
        quantity = request.POST['quantity']
        grade = request.POST['grade']
        center = request.POST['center']
        
        try:
            farmer = Farmer.objects.get(member_no=member_no)
            delivery = Delivery.objects.create(
                farmer=farmer,
                quantity=quantity,
                grade=grade,
                center=center,
                date=timezone.now().date()
            )
            messages.success(request, f'✅ Delivery recorded for {farmer.full_name}')
        except Farmer.DoesNotExist:
            messages.error(request, '❌ Farmer not found. Check member number.')
    
    return render(request, 'farmers/staff_delivery.html')

@login_required
def download_statement(request):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        farmer = request.user.farmer
        deliveries = Delivery.objects.filter(farmer=farmer).order_by('-date')
        payments = Payment.objects.filter(farmer=farmer).order_by('-payment_date')
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3d2f')
        )
        story.append(Paragraph(f"Karuhiu Utheri Cooperative", title_style))
        story.append(Paragraph(f"Statement for: {farmer.full_name} (Member #{farmer.member_no})", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        total_quantity = deliveries.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_value = sum(d.total_amount() for d in deliveries)
        total_paid = payments.filter(status='paid').aggregate(Sum('net_amount'))['net_amount__sum'] or 0
        
        story.append(Paragraph(f"Total Deliveries: {total_quantity} kg", styles['Normal']))
        story.append(Paragraph(f"Total Value: KSH {total_value:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Total Paid: KSH {total_paid:,.2f}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Deliveries table
        story.append(Paragraph("Delivery History", styles['Heading3']))
        if deliveries:
            data = [['Date', 'Quantity (kg)', 'Grade', 'Center', 'Amount (KSH)']]
            for d in deliveries[:20]:
                data.append([
                    d.date.strftime('%Y-%m-%d'),
                    str(d.quantity),
                    d.grade,
                    d.center,
                    f"{d.total_amount():,.2f}"
                ])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3d2f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f'statement_{farmer.member_no}.pdf')
        
    except Farmer.DoesNotExist:
        return redirect('dashboard')
    except ImportError:
        messages.error(request, 'PDF library not installed. Please install reportlab.')
        return redirect('dashboard')
