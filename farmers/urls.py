from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Farmer dashboard and features
    path('dashboard/', views.dashboard, name='dashboard'),
    path('yield/', views.yield_history, name='yield_history'),
    path('payments/', views.payment_history, name='payment_history'),
    path('statement/', views.download_statement, name='statement'),
    path('announcements/', views.announcements, name='announcements'),
    
    # Search feature
    path('search/', views.search_farmer, name='search'),
    
    # Staff only features
    path('staff/delivery/', views.staff_delivery, name='staff_delivery'),
]
