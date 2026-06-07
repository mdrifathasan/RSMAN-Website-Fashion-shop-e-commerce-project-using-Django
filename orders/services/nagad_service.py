import json
import requests
import base64
import hashlib
import time
from datetime import datetime
from django.conf import settings

class NagadPayment:
    def __init__(self):
        self.mode = getattr(settings, 'NAGAD_MODE', 'sandbox')  # sandbox or live
        self.merchant_id = getattr(settings, 'NAGAD_MERCHANT_ID', '683002007104225')
        self.merchant_number = getattr(settings, 'NAGAD_MERCHANT_NUMBER', '01770618515')
        
        # For development, use mock responses
        self.is_mock = not self.merchant_id or self.merchant_id == '683002007104225'
        
        if self.mode == 'sandbox':
            self.base_url = 'https://api.mynagad.com'
        else:
            self.base_url = 'https://api.mynagad.com'
        
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        self.callback_url = f"{site_url}/orders/nagad/callback/"
    
    def generate_random_string(self, length=20):
        """Generate random string for order ID"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def create_payment(self, amount, order_id, mobile_number):
        """Create Nagad payment"""
        # For development without real credentials, return mock response
        if self.is_mock:
            mock_payment_id = f"NAGAD_MOCK_{int(time.time())}_{order_id}"
            return {
                'success': True,
                'payment_id': mock_payment_id,
                'callback_url': f"/orders/nagad/mock/{mock_payment_id}/?order_id={order_id}",
                'order_id': f"NAGAD_ORDER_{order_id}",
                'message': 'Mock Nagad payment initiated'
            }
        
        try:
            # Generate order ID for Nagad
            nagad_order_id = f"NAGAD_{order_id}_{int(time.time())}"
            
            # In real implementation, you would:
            # 1. Get initialization token
            # 2. Create payment request
            # 3. Get callback URL
            
            # For now, return mock for development
            return {
                'success': True,
                'payment_id': f"NAGAD_{int(time.time())}",
                'callback_url': f"{self.callback_url}?payment_id=NAGAD_{int(time.time())}",
                'order_id': nagad_order_id,
                'message': 'Nagad payment initiated'
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id):
        """Verify Nagad payment"""
        # For development, return mock response
        if self.is_mock or 'MOCK' in payment_id:
            return {
                'success': True,
                'status': 'COMPLETED',
                'transaction_id': f"TRX_MOCK_{int(time.time())}",
                'order_id': f"NAGAD_ORDER_MOCK",
                'amount': '100.00',
                'message': 'Mock payment verified successfully'
            }
        
        try:
            # In real implementation, verify with Nagad API
            return {
                'success': True,
                'status': 'COMPLETED',
                'transaction_id': payment_id,
                'order_id': f"NAGAD_ORDER_{payment_id}",
                'amount': '100.00',
                'message': 'Payment verified successfully'
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }