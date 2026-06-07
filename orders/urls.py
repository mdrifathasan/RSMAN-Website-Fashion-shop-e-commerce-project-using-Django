# orders/urls.py - COMPLETE FIXED VERSION
from django.urls import path
from . import views

urlpatterns = [
    # Main order URLs
    path('place_order/', views.place_order, name='place_order'),
    path('order_complete/', views.order_complete, name='order_complete'),
    
    # Cash on Delivery URLs - ADD THESE
    path('payment-methods/<str:order_id>/', views.payment_methods, name='payment_methods'),
    path('confirm-cod/<str:order_id>/', views.confirm_cash_on_delivery, name='confirm_cash_on_delivery'),
    
    # Keep simplified payments function for backward compatibility
    path('payments/', views.payments, name='payments'),
]