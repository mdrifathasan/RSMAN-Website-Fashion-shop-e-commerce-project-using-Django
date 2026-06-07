from django.urls import path
from .views import dashboard_view, generate_pdf_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('generate-pdf/', generate_pdf_view, name='generate_pdf'),
]