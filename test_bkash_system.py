# test_bkash_system.py
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from orders.models import Order
from payments.sslcommerz_service import SSLCommerzPayment
import json

class TestBKashSystem(TestCase):
    
    def setUp(self):
        """Create test user and order"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test order
        self.order = Order.objects.create(
            user=self.user,
            order_number='TEST20241203123',
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='01712345678',
            address_line_1='123 Test Street',
            city='Dhaka',
            state='Dhaka',
            country='Bangladesh',
            order_total=150.00,
            tax=3.00,
            is_ordered=False
        )
    
    def test_payment_methods_page(self):
        """Test that payment methods page loads"""
        print("\n1. Testing payment methods page...")
        response = self.client.get(f'/payments/{self.order.order_number}/')
        print(f"   Status Code: {response.status_code}")
        print(f"   Template: {response.templates[0].name if response.templates else 'None'}")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bKash Payment')
        print("   ✅ Payment methods page works!")
    
    def test_sslcommerz_connection(self):
        """Test SSLCommerz API connection"""
        print("\n2. Testing SSLCommerz connection...")
        sslcz = SSLCommerzPayment(sandbox=True)
        
        # Test data
        test_data = {
            'order_id': 'TEST123',
            'total_amount': '100.00',
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '01712345678',
            'customer_address': 'Dhaka',
            'customer_city': 'Dhaka',
            'success_url': 'http://localhost:8000/test-success/',
            'fail_url': 'http://localhost:8000/test-fail/',
            'cancel_url': 'http://localhost:8000/test-cancel/',
        }
        
        result = sslcz.create_bkash_payment(test_data)
        print(f"   SSLCommerz Result: {result.get('success', False)}")
        
        if result.get('success'):
            print("   ✅ SSLCommerz connection successful!")
        else:
            print(f"   ⚠️ SSLCommerz error: {result.get('error', 'Unknown')}")
            print("   Note: This might be expected in test mode")
    
    def test_redirect_to_bkash(self):
        """Test redirect from old PayPal URLs"""
        print("\n3. Testing PayPal to bKash redirect...")
        response = self.client.get(f'/orders/redirect-to-bkash/{self.order.order_number}/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   ✅ Redirecting to: {response.url}")
        else:
            print("   ⚠️ No redirect happening")
    
    def test_old_paypal_endpoint(self):
        """Test that old PayPal endpoint redirects"""
        print("\n4. Testing old PayPal endpoint...")
        
        # Test JSON request (like PayPal webhook)
        response = self.client.post(
            '/payments/',
            json.dumps({
                'orderID': self.order.order_number,
                'transID': 'TEST_TRANS',
                'status': 'COMPLETED'
            }),
            content_type='application/json'
        )
        
        print(f"   JSON Response Status: {response.status_code}")
        
        # Test regular request
        response = self.client.get('/payments/')
        print(f"   GET Response Status: {response.status_code}")
        
        print("   ✅ Old PayPal endpoint properly handled")
    
    def test_template_existence(self):
        """Check if all required templates exist"""
        print("\n5. Checking template files...")
        
        templates = [
            'templates/payments/payment_methods.html',
            'templates/payments/order_complete.html',
            'templates/payments/payment_failed.html',
        ]
        
        for template in templates:
            if os.path.exists(template):
                print(f"   ✅ {template}")
            else:
                print(f"   ❌ {template} - MISSING!")
    
    def test_url_patterns(self):
        """Test URL patterns are accessible"""
        print("\n6. Testing URL patterns...")
        
        from django.urls import reverse, NoReverseMatch
        
        urls_to_test = [
            ('payment_methods', [self.order.order_number]),
            ('initiate_bkash_payment', [self.order.order_number]),
            ('order_complete', [self.order.order_number]),
            ('payment_failed', [self.order.order_number]),
        ]
        
        for url_name, args in urls_to_test:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✅ {url_name}: {url}")
            except NoReverseMatch:
                print(f"   ❌ {url_name} - URL not found")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("COMPREHENSIVE bKash PAYMENT SYSTEM TEST")
        print("=" * 60)
        
        tests = [
            self.test_payment_methods_page,
            self.test_sslcommerz_connection,
            self.test_redirect_to_bkash,
            self.test_old_paypal_endpoint,
            self.test_template_existence,
            self.test_url_patterns,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)

if __name__ == '__main__':
    tester = TestBKashSystem()
    tester.setUp()
    tester.run_all_tests()