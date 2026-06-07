from django.shortcuts import render 
from django.http import HttpResponse 
from django.utils import timezone 
from django.contrib.admin.views.decorators import staff_member_required 
import csv

from orders.models import Payment 
 
@staff_member_required 
def dashboard_view(request): 
    # Import models here to avoid circular imports 
    try: 
        from accounts.models import Account 
        from store.models import Product, ReviewRating 
        from orders.models import Order 
        from category.models import Category 
 
        context = { 
            'total_products': Product.objects.count(), 
            'total_categories': Category.objects.count(), 
            'total_users': Account.objects.count(), 
            'total_orders': Order.objects.count(), 
            'total_reviews': ReviewRating.objects.count(),
            'total_payments': Payment.objects.count()
        } 
    except: 
        # If models don't exist yet, show basic dashboard 
        context = { 
            'total_products': 0, 
            'total_categories': 0, 
            'total_users': 0, 
            'total_orders': 0, 
            'total_reviews': 0, 
        } 
 
    return render(request, 'admin/dashboard.html', context) 
 
@staff_member_required 
def generate_pdf_view(request): 
    # Get report type 
    report_type = request.GET.get('type', 'dashboard') 
 
    # Create CSV response 
    response = HttpResponse(content_type='text/csv') 
    response['Content-Disposition'] = f'attachment; filename="greatkart_{report_type}_report_{timezone.now().strftime("%%Y%%m%%d_%%H%%M%%S")}.csv"' 
 
    writer = csv.writer(response) 
    writer.writerow(['GreatKart Report', report_type.title()]) 
    writer.writerow(['Generated on', timezone.now().strftime('%%Y-%%m-%%d %%H:%%M:%%S')]) 
    writer.writerow([])  # Empty row 
 
    try: 
        from accounts.models import Account 
        from store.models import Product 
        from orders.models import Order 
        from category.models import Category 
 
        writer.writerow(['Metric', 'Value']) 
 
        if report_type in ['dashboard', 'overview', 'all']: 
            writer.writerow(['Total Products', Product.objects.count()]) 
            writer.writerow(['Total Categories', Category.objects.count()]) 
            writer.writerow(['Total Users', Account.objects.count()]) 
            writer.writerow(['Total Orders', Order.objects.count()]) 
        elif report_type == 'sales': 
            writer.writerow(['Total Orders', Order.objects.count()]) 
        elif report_type == 'inventory': 
            writer.writerow(['Total Products', Product.objects.count()]) 
        elif report_type == 'users': 
            writer.writerow(['Total Users', Account.objects.count()]) 
 
    except: 
        writer.writerow(['Error', 'Data not available']) 
 
    return response 
