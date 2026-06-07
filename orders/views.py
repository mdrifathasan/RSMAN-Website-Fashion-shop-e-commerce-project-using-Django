# orders/views.py - COMPLETE FIXED VERSION WITH CASH ON DELIVERY

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct, MobilePayment
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# ===== CASH ON DELIVERY VIEWS =====
@login_required
def payment_methods(request, order_id):
    """
    Show ONLY Cash on Delivery payment method
    """
    try:
        order = Order.objects.get(order_number=order_id, user=request.user)
        
        # Check if order is already paid/processed
        if order.is_ordered:
            return redirect('order_complete')
        
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
        return redirect('cart')
    except Exception as e:
        print(f"Error: {e}")
        return redirect('cart')

@login_required
def confirm_cash_on_delivery(request, order_id):
    """
    Handle Cash on Delivery payment confirmation
    """
    try:
        order = Order.objects.get(order_number=order_id, user=request.user)
        
        # Check if order is already processed
        if order.is_ordered:
            return redirect('order_complete')
        
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
            created_at=timezone.now(),
        )
        
        # Link payment to order
        order.payment = payment
        order.status = 'Confirmed'
        order.is_ordered = True
        order.save()
        
        # Move cart items to order products
        cart_items = CartItem.objects.filter(user=request.user)
        
        for item in cart_items:
            orderproduct = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True
            )
            
            # Add variations if any
            product_variations = item.variations.all()
            orderproduct.variations.set(product_variations)
            
            # Reduce stock
            product = item.product
            if hasattr(product, 'stock'):
                product.stock -= item.quantity
                product.save()
        
        # Clear cart
        cart_items.delete()
        
        # Send order received email
        try:
            mail_subject = 'Thank you for your order! (Cash on Delivery)'
            message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
        except:
            pass  # Continue even if email fails
        
        # FIXED: Redirect to order complete page
        return redirect(f'{reverse("order_complete")}?order_number={order.order_number}&payment_id={payment.payment_id}')
        
    except Order.DoesNotExist:
        return redirect('cart')
    except Exception as e:
        print(f"Error in confirm_cash_on_delivery: {e}")
        return redirect('payment_methods', order_id=order_id)

# ===== YOUR EXISTING place_order FUNCTION (UPDATED) =====
@login_required
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = ( 5 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Redirect to Cash on Delivery payment page
            return redirect('payment_methods', order_id=data.order_number)
    else:
        return redirect('checkout')

# ===== YOUR EXISTING order_complete FUNCTION =====
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'is_cod': payment.payment_method == 'Cash on Delivery',
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    except Exception as e:
        print(f"Error in order_complete: {e}")
        return redirect('store')

# ===== OPTIONAL: SIMPLIFIED payments FUNCTION FOR BACKWARD COMPATIBILITY =====
@csrf_exempt
@login_required
def payments(request):
    """
    Simplified payments function for backward compatibility
    Now only handles Cash on Delivery confirmation
    """
    try:
        # Get order from request
        body = json.loads(request.body)
        order = Order.objects.get(
            user=request.user, 
            is_ordered=False, 
            order_number=body['orderID']
        )
        
        # Create Cash on Delivery payment
        payment = Payment(
            user=request.user,
            payment_id=f"COD-{order.order_number}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            payment_method='Cash on Delivery',
            amount_paid=str(order.order_total),
            status='AWAITING_PAYMENT',
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.status = 'Confirmed'
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            if hasattr(product, 'stock'):
                product.stock -= item.quantity
                product.save()

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order received email to customer
        try:
            mail_subject = 'Thank you for your order! (Cash on Delivery)'
            message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
        except:
            pass  # Continue even if email fails

        # Return order data
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)