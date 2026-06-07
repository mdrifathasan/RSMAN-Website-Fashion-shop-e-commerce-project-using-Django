import requests
import json
import time
from django.conf import settings

class BKashPayment:
    def __init__(self):
        self.mode = getattr(settings, 'BKASH_MODE', 'sandbox')
        self.app_key = getattr(settings, 'BKASH_APP_KEY', '')
        self.app_secret = getattr(settings, 'BKASH_APP_SECRET', '')
        self.username = getattr(settings, 'BKASH_USERNAME', '')
        self.password = getattr(settings, 'BKASH_PASSWORD', '')
        
        if self.mode == 'sandbox':
            self.base_url = 'https://tokenized.sandbox.bka.sh/v1.2.0-beta'
        else:
            self.base_url = 'https://tokenized.pay.bka.sh/v1.2.0-beta'
    
    def get_token(self):
        """Get bKash authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/tokenized/checkout/token/grant",
                json={
                    "app_key": self.app_key,
                    "app_secret": self.app_secret
                },
                headers={
                    "accept": "application/json",
                    "content-type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('id_token')
            return None
        except Exception as e:
            print(f"bKash token error: {e}")
            return None
    
    def create_payment(self, amount, order_id, mobile_number):
        """Create bKash payment"""
        # For development without real credentials, return mock response
        if not self.app_key or not self.app_secret:
            return {
                'success': True,
                'payment_id': f"BKASH_MOCK_{int(time.time())}_{order_id}",
                'bkash_url': f"/orders/bkash/mock/BKASH_MOCK_{int(time.time())}_{order_id}/?order_id={order_id}",
                'message': 'Mock bKash payment initiated'
            }
        
        token = self.get_token()
        if not token:
            return {
                'success': False,
                'error': 'Failed to authenticate with bKash'
            }
        
        try:
            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            
            response = requests.post(
                f"{self.base_url}/tokenized/checkout/create",
                json={
                    "mode": "0011",
                    "payerReference": mobile_number,
                    "callbackURL": f"{site_url}/orders/bkash/callback/",
                    "amount": str(amount),
                    "currency": "BDT",
                    "intent": "sale",
                    "merchantInvoiceNumber": f"ORD{order_id}"
                },
                headers={
                    "accept": "application/json",
                    "Authorization": token,
                    "X-APP-Key": self.app_key,
                    "content-type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('statusCode') == '0000':
                    return {
                        'success': True,
                        'payment_id': data.get('paymentID'),
                        'bkash_url': data.get('bkashURL'),
                        'message': 'Payment initiated successfully'
                    }
            
            return {
                'success': False,
                'error': 'Failed to create bKash payment'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_payment(self, payment_id):
        """Execute bKash payment"""
        # For development without real credentials, return mock response
        if not self.app_key or not self.app_secret:
            return {
                'success': True,
                'status': '0000',
                'transaction_id': f"TRX_MOCK_{int(time.time())}",
                'amount': '100.00',
                'message': 'Mock payment executed successfully'
            }
        
        token = self.get_token()
        if not token:
            return {
                'success': False,
                'error': 'Failed to authenticate with bKash'
            }
        
        try:
            response = requests.post(
                f"{self.base_url}/tokenized/checkout/execute",
                json={"paymentID": payment_id},
                headers={
                    "accept": "application/json",
                    "Authorization": token,
                    "X-APP-Key": self.app_key,
                    "content-type": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': data.get('statusCode') == '0000',
                    'status': data.get('statusCode'),
                    'transaction_id': data.get('trxID'),
                    'amount': data.get('amount'),
                    'message': data.get('statusMessage')
                }
            
            return {
                'success': False,
                'error': 'Failed to execute payment'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }