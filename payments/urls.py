# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Cash on Delivery URLs
    path('payment-methods/<str:order_id>/', views.payment_methods, name='payment_methods'),
    path('confirm-cod/<str:order_id>/', views.confirm_cash_on_delivery, name='confirm_cash_on_delivery'),
    path('order-complete/<str:order_id>/', views.order_complete, name='order_complete'),
    
    # Optional: Payment failed page (for consistency)
    path('payment-failed/<str:order_id>/', views.payment_failed, name='payment_failed'),
]