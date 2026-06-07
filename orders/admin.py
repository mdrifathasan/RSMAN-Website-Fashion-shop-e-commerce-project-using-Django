from django.contrib import admin
from .models import Payment, Order, OrderProduct, DeliveryTracking, MobilePayment
from django.utils.html import format_html

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered', 'variations_display')
    extra = 0
    can_delete = False
    
    def variations_display(self, obj):
        return ", ".join([str(v) for v in obj.variations.all()])
    variations_display.short_description = 'Variations'

class DeliveryTrackingInline(admin.StackedInline):
    model = DeliveryTracking
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ('tracking_number', 'courier_name', 'estimated_delivery', 'get_tracking_status')
    
    def has_add_permission(self, request, obj=None):
        return False

class MobilePaymentInline(admin.TabularInline):
    model = MobilePayment
    extra = 0
    max_num = 1
    can_delete = False
    readonly_fields = ('payment_gateway', 'mobile_number', 'amount', 'status', 'transaction_id')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'get_payment_method', 'get_status', 'amount_paid', 'created_at', 'is_verified', 'courier_display')
    list_filter = ('payment_method', 'status', 'is_verified', 'created_at')
    search_fields = ('payment_id', 'user__email', 'transaction_id', 'mobile_number')
    readonly_fields = ('payment_id', 'user', 'payment_method', 'amount_paid', 'created_at', 'transaction_id', 'mobile_number')
    list_per_page = 20
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
        }),
        ('Payment Gateway Details', {
            'fields': ('payment_gateway', 'transaction_id', 'mobile_number', 'is_verified', 'verification_time'),
            'classes': ('collapse',)
        }),
        ('Cash on Delivery Details', {
            'fields': ('courier_name', 'expected_delivery_date', 'delivered_at', 'delivery_notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_payment_method(self, obj):
        if obj.payment_method == 'Cash on Delivery':
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ {}</span>', obj.payment_method)
        return obj.payment_method
    get_payment_method.short_description = 'Payment Method'
    
    def get_status(self, obj):
        status_colors = {
            'PENDING': 'warning',
            'AWAITING_PAYMENT': 'info',
            'PROCESSING': 'primary',
            'COMPLETED': 'success',
            'FAILED': 'danger',
            'REFUNDED': 'secondary',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status)
    get_status.short_description = 'Status'
    
    def courier_display(self, obj):
        if obj.payment_method == 'Cash on Delivery' and obj.courier_name:
            return format_html('<span style="color: #007bff;">{}</span>', obj.courier_name)
        return '-'
    courier_display.short_description = 'Courier'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'get_status', 'is_ordered', 'created_at', 'payment_method_display', 'courier_service']
    list_filter = ['status', 'is_ordered', 'courier_service', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email', 'tracking_number']
    list_per_page = 20
    readonly_fields = ('order_number', 'user', 'payment', 'order_total', 'tax', 'created_at', 'updated_at')
    inlines = [OrderProductInline, DeliveryTrackingInline, MobilePaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'is_ordered', 'order_total', 'tax')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Shipping Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'country')
        }),
        ('Delivery Information', {
            'fields': ('courier_service', 'tracking_number')
        }),
        ('Additional Information', {
            'fields': ('order_note', 'ip', 'paypal_order_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    def get_status(self, obj):
        status_colors = {
            'New': 'secondary',
            'Pending': 'warning',
            'Confirmed': 'info',
            'Processing': 'primary',
            'Shipped': 'info',
            'Out for Delivery': 'primary',
            'Delivered': 'success',
            'Completed': 'success',
            'Cancelled': 'danger',
            'Refunded': 'secondary',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status)
    get_status.short_description = 'Status'
    
    def payment_method_display(self, obj):
        if obj.payment:
            if obj.payment.payment_method == 'Cash on Delivery':
                return format_html('<span style="color: #28a745; font-weight: bold;">✓ {}</span>', obj.payment.payment_method)
            return obj.payment.payment_method
        return '-'
    payment_method_display.short_description = 'Payment Method'
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='Confirmed')
        self.message_user(request, f'{updated} orders marked as Confirmed.')
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='Shipped')
        self.message_user(request, f'{updated} orders marked as Shipped.')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.mark_as_delivered()
        self.message_user(request, f'{queryset.count()} orders marked as Delivered.')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order_link', 'courier_name', 'tracking_status', 'estimated_delivery', 'is_delivered', 'delivered_date')
    list_filter = ('courier_name', 'is_delivered', 'is_shipped', 'created_at')
    search_fields = ('tracking_number', 'order__order_number', 'courier_name')
    readonly_fields = ('tracking_number', 'order', 'courier_name', 'get_tracking_status', 'created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Tracking Information', {
            'fields': ('tracking_number', 'order', 'courier_name', 'courier_contact', 'estimated_delivery')
        }),
        ('Tracking Milestones', {
            'fields': (
                ('is_picked_up', 'pickup_date'),
                ('is_shipped', 'shipped_date'),
                ('is_out_for_delivery', 'out_for_delivery_date'),
                ('is_delivered', 'delivered_date')
            )
        }),
        ('Delivery Information', {
            'fields': ('delivery_person_name', 'delivery_person_contact', 'delivery_notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_to_picked_up', 'update_to_shipped', 'update_to_out_for_delivery', 'update_to_delivered']
    
    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">#{}</a>', obj.order.id, obj.order.order_number)
    order_link.short_description = 'Order Number'
    
    def tracking_status(self, obj):
        status = obj.get_tracking_status()
        status_colors = {
            'Processing': 'warning',
            'Picked Up': 'info',
            'Shipped': 'primary',
            'Out for Delivery': 'info',
            'Delivered': 'success',
        }
        color = status_colors.get(status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, status)
    tracking_status.short_description = 'Current Status'
    
    def update_to_picked_up(self, request, queryset):
        for tracking in queryset:
            tracking.update_status('picked_up')
        self.message_user(request, f'{queryset.count()} tracking records updated to Picked Up.')
    update_to_picked_up.short_description = "Mark as Picked Up"
    
    def update_to_shipped(self, request, queryset):
        for tracking in queryset:
            tracking.update_status('shipped')
        self.message_user(request, f'{queryset.count()} tracking records updated to Shipped.')
    update_to_shipped.short_description = "Mark as Shipped"
    
    def update_to_out_for_delivery(self, request, queryset):
        for tracking in queryset:
            tracking.update_status('out_for_delivery')
        self.message_user(request, f'{queryset.count()} tracking records updated to Out for Delivery.')
    update_to_out_for_delivery.short_description = "Mark as Out for Delivery"
    
    def update_to_delivered(self, request, queryset):
        for tracking in queryset:
            tracking.update_status('delivered')
        self.message_user(request, f'{queryset.count()} tracking records updated to Delivered.')
    update_to_delivered.short_description = "Mark as Delivered"

@admin.register(MobilePayment)
class MobilePaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_gateway', 'order_link', 'user', 'mobile_number', 'amount', 'get_status', 'transaction_id', 'created_at')
    list_filter = ('payment_gateway', 'status', 'created_at')
    search_fields = ('transaction_id', 'mobile_number', 'order__order_number', 'user__email')
    readonly_fields = ('order', 'user', 'payment_gateway', 'mobile_number', 'amount', 'transaction_id', 'created_at', 'updated_at')
    list_per_page = 20
    
    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">#{}</a>', obj.order.id, obj.order.order_number)
    order_link.short_description = 'Order Number'
    
    def get_status(self, obj):
        status_colors = {
            'pending': 'warning',
            'initiated': 'info',
            'completed': 'success',
            'failed': 'danger',
            'expired': 'secondary',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status.capitalize())
    get_status.short_description = 'Status'

@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'product', 'user', 'quantity', 'product_price', 'ordered', 'created_at')
    list_filter = ('ordered', 'created_at')
    search_fields = ('order__order_number', 'product__product_name', 'user__email')
    readonly_fields = ('order', 'payment', 'user', 'product', 'variations_display', 'quantity', 'product_price', 'ordered')
    list_per_page = 20
    
    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">#{}</a>', obj.order.id, obj.order.order_number)
    order_link.short_description = 'Order Number'
    
    def variations_display(self, obj):
        return ", ".join([str(v) for v in obj.variations.all()])
    variations_display.short_description = 'Variations'