import json
import requests
import hashlib
import uuid
from django.conf import settings
from django.urls import reverse

class SSLCommerzPayment:
    def __init__(self):
        self.store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', 'testbox')
        self.store_passwd = getattr(settings, 'SSLCOMMERZ_STORE_PASSWD', 'qwerty')
        self.mode = getattr(settings, 'SSLCOMMERZ_MODE', 'sandbox')  # sandbox or live
        
        if self.mode == 'sandbox':
            self.base_url = 'https://sandbox.sslcommerz.com'
        else:
            self.base_url = 'https://securepay.sslcommerz.com'
    
    def create_payment(self, order, request):
        """Create SSLCommerz payment session"""
        # Generate unique transaction ID
        tran_id = f"SSL_{order.order_number}_{uuid.uuid4().hex[:8]}"
        
        # Calculate total amount
        total_amount = float(order.order_total)
        
        # Get site URL for callbacks
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        
        # Build post data
        post_data = {
            'store_id': self.store_id,
            'store_passwd': self.store_passwd,
            'total_amount': f"{total_amount:.2f}",
            'currency': 'BDT',
            'tran_id': tran_id,
            'success_url': f"{site_url}/orders/ssl/success/",
            'fail_url': f"{site_url}/orders/ssl/fail/",
            'cancel_url': f"{site_url}/orders/ssl/cancel/",
            'emi_option': 0,
            'cus_name': f"{order.first_name} {order.last_name}",
            'cus_email': order.email,
            'cus_phone': order.phone,
            'cus_add1': order.address_line_1[:50] if order.address_line_1 else '',
            'cus_city': order.city[:50] if order.city else '',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'product_name': f'Order #{order.order_number}',
            'product_category': 'General',
            'product_profile': 'general',
            'value_a': order.order_number,  # Custom field for order number
            'value_b': str(order.user.id),  # Custom field for user ID
        }
        
        # Add optional fields if available
        if order.address_line_2:
            post_data['cus_add2'] = order.address_line_2[:50]
        if order.state:
            post_data['cus_state'] = order.state[:50]
        
        try:
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php",
                data=post_data,
                verify=False  # Set to True in production with proper SSL certs
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'SUCCESS':
                    return {
                        'success': True,
                        'sessionkey': result.get('sessionkey'),
                        'gateway_page_url': result.get('GatewayPageURL'),
                        'tran_id': tran_id,
                        'message': result.get('message')
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('failedreason', 'Payment initiation failed')
                    }
            else:
                return {
                    'success': False,
                    'error': f'SSLCommerz API error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, tran_id):
        """Verify SSLCommerz payment"""
        try:
            response = requests.post(
                f"{self.base_url}/validator/api/validationserverAPI.php",
                data={
                    'store_id': self.store_id,
                    'store_passwd': self.store_passwd,
                    'tran_id': tran_id,
                    'format': 'json'
                },
                verify=False
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'tran_id': result.get('tran_id'),
                    'amount': result.get('amount'),
                    'bank_tran_id': result.get('bank_tran_id'),
                    'card_type': result.get('card_type'),
                    'card_no': result.get('card_no'),
                    'card_issuer': result.get('card_issuer'),
                    'message': result.get('message')
                }
            else:
                return {
                    'success': False,
                    'error': f'Verification failed: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }