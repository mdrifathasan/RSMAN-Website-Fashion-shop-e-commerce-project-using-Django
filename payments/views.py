# payments/views.py - COMPLETE FIXED VERSION
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import json
from datetime import timedelta

# Import your models
from orders.models import Order, Payment, OrderProduct, DeliveryTracking
from carts.models import CartItem

# CASH ON DELIVERY ONLY VIEWS

@login_required(login_url='login')
def payment_methods(request, order_id):
    """
    Show ONLY Cash on Delivery payment method
    """
    try:
        order = Order.objects.get(order_number=order_id, user=request.user)
        
        # Check if order is already paid/processed
        if order.is_ordered:
            messages.warning(request, 'This order has already been processed.')
            return redirect('order_complete', order_id=order.order_number)
        
        # Calculate totals
        tax = order.tax if hasattr(order, 'tax') else order.order_total * Decimal('0.02')
        grand_total = order.order_total + tax
        
        context = {
            'order': order,
            'tax': tax,
            'grand_total': grand_total,
            'order_total_gbp': order.order_total,
        }
        
        return render(request, 'payments/payment_methods.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('cart')

@login_required(login_url='login')
def confirm_cash_on_delivery(request, order_id):
    """
    Handle Cash on Delivery payment confirmation
    """
    try:
        order = Order.objects.get(order_number=order_id, user=request.user)
        
        # Check if order is already processed
        if order.is_ordered:
            messages.warning(request, 'This order has already been processed.')
            return redirect('order_complete', order_id=order.order_number)
        
        # Calculate totals
        tax = order.tax if hasattr(order, 'tax') else order.order_total * Decimal('0.02')
        grand_total = order.order_total + tax
        
        # Create payment record for Cash on Delivery
        payment = Payment.objects.create(
            user=request.user,
            payment_id=f"COD-{order.order_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            payment_method='Cash on Delivery',
            amount_paid=str(grand_total),
            status='AWAITING_PAYMENT',
            courier_name='Patahu Courier',
            expected_delivery_date=timezone.now().date() + timedelta(days=4),
            created_at=timezone.now(),
        )
        
        # Link payment to order
        order.payment = payment
        order.status = 'Confirmed'
        order.is_ordered = True
        order.courier_service = 'Patahu Courier'
        order.save()
        
        # Clear cart
        CartItem.objects.filter(user=request.user).delete()
        
        # Create delivery tracking record
        try:
            # Generate tracking number
            tracking_number = f"PATAHU-{order.order_number}-{timezone.now().strftime('%y%m%d')}"
            
            # Calculate estimated delivery (3-5 business days)
            estimated_date = timezone.now().date() + timedelta(days=4)
            
            DeliveryTracking.objects.create(
                order=order,
                tracking_number=tracking_number,
                courier_name='Patahu Courier',
                estimated_delivery=estimated_date
            )
            
            # Update order with tracking number
            order.tracking_number = tracking_number
            order.save()
            
        except Exception as e:
            print(f"Could not create tracking: {e}")
            # Continue even if tracking fails
        
        # Redirect to order complete page
        messages.success(request, 'Order confirmed successfully! You will pay via Cash on Delivery when you receive your order.')
        return redirect('order_complete', order_id=order.order_number)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found')
        return redirect('cart')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('payment_methods', order_id=order_id)

@login_required(login_url='login')
def order_complete(request, order_id):
    """
    Order completion page - MODIFIED for Cash on Delivery
    """
    try:
        order = get_object_or_404(Order, order_number=order_id, user=request.user)
        payment = order.payment if hasattr(order, 'payment') else None
        
        # Get ordered products
        try:
            ordered_products = OrderProduct.objects.filter(order=order)
            subtotal = sum(item.product_price * item.quantity for item in ordered_products)
        except:
            ordered_products = []
            subtotal = 0
        
        # Get delivery tracking if exists
        delivery_tracking = None
        try:
            delivery_tracking = DeliveryTracking.objects.get(order=order)
        except DeliveryTracking.DoesNotExist:
            pass
        
        context = {
            'order': order,
            'payment': payment,
            'ordered_products': ordered_products,
            'subtotal': subtotal,
            'transID': payment.payment_id if payment else 'N/A',
            'delivery_tracking': delivery_tracking,
            'is_cod': True,  # Always true for COD system
        }
        return render(request, 'payments/order_complete.html', context)
    except Exception as e:
        messages.error(request, f'Error loading order: {str(e)}')
        return redirect('store')

@login_required(login_url='login')
def payment_failed(request, order_id):
    """
    Payment failed page (for backward compatibility)
    """
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    return render(request, 'payments/payment_failed.html', {'order': order})

# REMOVE OR COMMENT OUT ALL OLD PAYMENT FUNCTIONS:
# - create_paypal_payment
# - execute_paypal_payment
# - paypal_payment_failed
# - initiate_bkash_payment
# - bkash_success, bkash_fail, bkash_cancel, bkash_ipn
# - etc.