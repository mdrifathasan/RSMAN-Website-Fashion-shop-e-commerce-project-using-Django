from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Fake admin login for honeypot
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    
    # Dashboard URLs - with specific prefix
    path('securelogin/dashboard/', include('dashboard.urls')),
    
    # Admin URLs
    path('securelogin/', admin.site.urls),
    
    # Main site URLs
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    
    # ADD THIS LINE - Payments URLs for Cash on Delivery
    path('payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)