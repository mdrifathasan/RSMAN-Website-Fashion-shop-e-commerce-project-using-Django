from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json

from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    
    # This method adds custom URLs to the admin
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='dashboard'),
            path('dashboard/generate-pdf/', self.admin_site.admin_view(self.generate_pdf_view), name='generate_pdf'),
        ]
        return my_urls + urls
    
    def dashboard_view(self, request):
        # Import models here to avoid circular imports
        try:
            from accounts.models import Account
            from store.models import Product, ReviewRating
            from orders.models import Order
            from category.models import Category
            
            # Calculate statistics
            context = {
                **self.admin_site.each_context(request),
                'title': 'Dashboard Overview',
                'total_products': Product.objects.count(),
                'total_categories': Category.objects.count(),
                'total_users': Account.objects.count(),
                'total_orders': Order.objects.count(),
                'total_reviews': ReviewRating.objects.count(),
            }
            
            return render(request, 'admin/dashboard.html', context)
            
        except ImportError as e:
            # If models don't exist yet, show basic dashboard
            context = {
                **self.admin_site.each_context(request),
                'title': 'Dashboard Overview',
                'total_products': 0,
                'total_categories': 0,
                'total_users': 0,
                'total_orders': 0,
                'total_reviews': 0,
            }
            return render(request, 'admin/dashboard.html', context)
    
    def generate_pdf_view(self, request):
        # Create PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Get report type
        report_type = request.GET.get('type', 'dashboard')
        
        # Add content to PDF
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, f"GreatKart {report_type.replace('_', ' ').title()} Report")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Try to import models for data
        y_position = 700
        
        try:
            from accounts.models import Account
            from store.models import Product
            from orders.models import Order
            from category.models import Category
            
            # Add summary data
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, y_position, "System Summary:")
            y_position -= 20
            
            p.setFont("Helvetica", 12)
            
            if report_type in ['dashboard', 'overview', 'all']:
                p.drawString(100, y_position, f"Total Products: {Product.objects.count()}")
                y_position -= 20
                p.drawString(100, y_position, f"Total Categories: {Category.objects.count()}")
                y_position -= 20
                p.drawString(100, y_position, f"Total Users: {Account.objects.count()}")
                y_position -= 20
                p.drawString(100, y_position, f"Total Orders: {Order.objects.count()}")
                y_position -= 20
            
            if report_type == 'sales':
                p.drawString(100, y_position, f"Total Orders: {Order.objects.count()}")
                y_position -= 20
                
            if report_type == 'inventory':
                p.drawString(100, y_position, f"Total Products: {Product.objects.count()}")
                y_position -= 20
                
            if report_type == 'users':
                p.drawString(100, y_position, f"Total Users: {Account.objects.count()}")
                y_position -= 20
                
        except ImportError:
            p.drawString(100, y_position, "Data not available")
            y_position -= 20
        
        # Save the PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        
        # Return PDF as response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="greatkart_{report_type}_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response

# Note: The @admin.register decorator above handles registration
# So we don't need admin.site.register() anymore