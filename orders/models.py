from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from datetime import timedelta
from django.utils import timezone

class Payment(models.Model):
    # PAYMENT METHOD CHOICES
    PAYMENT_METHOD_CHOICES = (
        ('Cash on Delivery', 'Cash on Delivery'),
        ('bKash', 'bKash'),
        ('Nagad', 'Nagad'),
        ('PayPal', 'PayPal'),
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
    )
    
    # PAYMENT STATUS CHOICES
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('AWAITING_PAYMENT', 'Awaiting Payment'),  # For COD - Not paid yet
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    )
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    
    # UPDATED: Use choices for payment method
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    
    amount_paid = models.CharField(max_length=100)  # this is the total amount paid
    
    # UPDATED: Use choices for status
    status = models.CharField(max_length=100, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    # Add bKash/Nagad specific fields
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # bKash/Nagad transaction ID
    payment_gateway = models.CharField(max_length=50, default='PayPal')  # 'bKash', 'Nagad', 'PayPal'
    
    # Status fields for bKash/Nagad
    is_verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(blank=True, null=True)
    
    # NEW: Cash on Delivery specific fields
    courier_name = models.CharField(max_length=100, blank=True, null=True)  # "Patahu Courier"
    expected_delivery_date = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.payment_gateway} - {self.payment_id}"
    
    def is_cod(self):
        return self.payment_method == 'Cash on Delivery'
    
    def mark_as_paid_on_delivery(self):
        """Mark payment as paid when delivered"""
        if self.is_cod():
            self.status = 'COMPLETED'
            self.delivered_at = timezone.now()
            self.save()


class Order(models.Model):
    # UPDATED STATUS CHOICES
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),  # Added for COD confirmation
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),  # Added
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    
    # field for PayPal integration
    paypal_order_id = models.CharField(max_length=100, blank=True, null=True)
    
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    
    # UPDATED: Added more status options
    status = models.CharField(max_length=20, choices=STATUS, default='New')
    
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # NEW: Delivery tracking reference
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    courier_service = models.CharField(max_length=100, blank=True, null=True, default='Patahu Courier')

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    # NEW: Check if order is Cash on Delivery
    def is_cod(self):
        return self.payment and self.payment.payment_method == 'Cash on Delivery'
    
    # NEW: Get estimated delivery date
    def get_estimated_delivery(self):
        if self.payment and self.payment.expected_delivery_date:
            return self.payment.expected_delivery_date
        # Default: 4 days from order date
        return (self.created_at + timedelta(days=4)).date()
    
    # NEW: Mark as delivered for COD
    def mark_as_delivered(self):
        self.status = 'Delivered'
        self.save()
        if self.payment and self.payment.is_cod():
            self.payment.mark_as_paid_on_delivery()

    def __str__(self):
        return f"Order #{self.order_number} - {self.first_name}"


# NEW: Delivery Tracking Model (Optional but recommended)
class DeliveryTracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_tracking')
    tracking_number = models.CharField(max_length=100, unique=True)
    courier_name = models.CharField(max_length=100, default='Patahu Courier')
    courier_contact = models.CharField(max_length=20, blank=True, null=True)
    estimated_delivery = models.DateField()
    
    # Tracking milestones
    pickup_date = models.DateTimeField(blank=True, null=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    out_for_delivery_date = models.DateTimeField(blank=True, null=True)
    delivered_date = models.DateTimeField(blank=True, null=True)
    
    # Tracking status flags
    is_picked_up = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_out_for_delivery = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    
    delivery_notes = models.TextField(blank=True, null=True)
    delivery_person_name = models.CharField(max_length=100, blank=True, null=True)
    delivery_person_contact = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tracking #{self.tracking_number} - Order #{self.order.order_number}"
    
    def get_tracking_status(self):
        if self.is_delivered:
            return 'Delivered'
        elif self.is_out_for_delivery:
            return 'Out for Delivery'
        elif self.is_shipped:
            return 'Shipped'
        elif self.is_picked_up:
            return 'Picked Up'
        else:
            return 'Processing'
    
    def update_status(self, status):
        """Update tracking status"""
        now = timezone.now()
        if status == 'picked_up':
            self.is_picked_up = True
            self.pickup_date = now
            self.order.status = 'Processing'
        elif status == 'shipped':
            self.is_shipped = True
            self.shipped_date = now
            self.order.status = 'Shipped'
        elif status == 'out_for_delivery':
            self.is_out_for_delivery = True
            self.out_for_delivery_date = now
            self.order.status = 'Out for Delivery'
        elif status == 'delivered':
            self.is_delivered = True
            self.delivered_date = now
            self.order.mark_as_delivered()
        
        self.save()
        self.order.save()


# Move MobilePayment AFTER Order since it references Order
class MobilePayment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_gateway = models.CharField(max_length=20, choices=[('bKash', 'bKash'), ('Nagad', 'Nagad')])
    mobile_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    verification_response = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.payment_gateway} - {self.mobile_number} - {self.amount}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name