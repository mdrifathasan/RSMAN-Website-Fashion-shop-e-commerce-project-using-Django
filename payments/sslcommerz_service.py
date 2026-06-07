# payments/sslcommerz_service.py - UPDATED VERSION
import requests
import json
import uuid
from datetime import datetime
from django.conf import settings

class SSLCommerzPayment:
    """
    SSLCommerz Payment Gateway Integration for bKash ONLY
    """
    
    def __init__(self, sandbox=True):
        self.sandbox = sandbox
        
        if sandbox:
            # SSLCommerz Sandbox Credentials (FREE for testing)
            self.store_id = "testbox"
            self.store_passwd = "qwerty"
            self.base_url = "https://sandbox.sslcommerz.com"
        else:
            # Production credentials
            self.store_id = settings.SSLCOMMERZ_STORE_ID
            self.store_passwd = settings.SSLCOMMERZ_STORE_PASSWORD
            self.base_url = "https://securepay.sslcommerz.com"
        
        # API endpoints
        self.init_url = f"{self.base_url}/gwprocess/v4/api.php"  # Updated to v4
        self.validation_url = f"{self.base_url}/validator/api/validationserverAPI.php"
    
    def create_bkash_payment(self, order_data):
        """
        Create bKash payment session with SSLCommerz
        """
        # Generate unique transaction ID
        tran_id = f"TXN{order_data['order_id']}{int(datetime.now().timestamp())}"
        
        # Prepare payment parameters for bKash ONLY
        post_data = {
            # Store credentials
            'store_id': self.store_id,
            'store_passwd': self.store_passwd,
            
            # Transaction details
            'total_amount': order_data['total_amount'],
            'currency': order_data.get('currency', 'BDT'),
            'tran_id': tran_id,
            
            # Success/Failure URLs - CRITICAL FIX HERE
            'success_url': order_data['success_url'],
            'fail_url': order_data['fail_url'],
            'cancel_url': order_data['cancel_url'],
            'ipn_url': order_data.get('ipn_url', ''),  # Server-to-server notification
            
            # Customer information
            'cus_name': order_data['customer_name'],
            'cus_email': order_data['customer_email'],
            'cus_add1': order_data.get('customer_address', 'N/A'),
            'cus_city': order_data.get('customer_city', 'N/A'),
            'cus_state': 'Dhaka',
            'cus_postcode': '1000',
            'cus_country': 'Bangladesh',
            'cus_phone': order_data['customer_phone'],
            'cus_fax': order_data['customer_phone'],
            
            # Shipping information (same as billing for bKash)
            'shipping_method': 'NO',
            'num_of_item': order_data.get('num_of_items', 1),
            'product_name': order_data.get('product_name', 'Order'),
            'product_category': 'Ecommerce',
            'product_profile': 'general',
            
            # bKash specific - Force bKash only
            'multi_card_name': 'bkash',
            
            # Additional parameters for better tracking
            'value_a': order_data['order_id'],  # Store order ID
            'value_b': 'bKash_Payment',
            'value_c': 'RSMAN_Ecommerce',
            'value_d': str(datetime.now().timestamp()),
            
            # Important flags
            'emi_option': 0,
            'emi_max_inst_option': 0,
            'emi_selected_inst': 0,
        }
        
        try:
            print(f"DEBUG: Sending to SSLCommerz: {post_data}")
            
            # Send request to SSLCommerz
            response = requests.post(self.init_url, data=post_data, timeout=30)
            print(f"DEBUG: SSLCommerz Response Status: {response.status_code}")
            print(f"DEBUG: SSLCommerz Response: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 'SUCCESS':
                return {
                    'success': True,
                    'sessionkey': result['sessionkey'],
                    'GatewayPageURL': result['GatewayPageURL'],
                    'tran_id': tran_id,
                    'bank_tran_id': result.get('bank_tran_id', ''),
                    'store_id': result.get('store_id', ''),
                }
            else:
                error_msg = result.get('failedreason', 'Payment initiation failed')
                if 'desc' in result:
                    error_msg += f" - {result['desc']}"
                return {
                    'success': False,
                    'error': error_msg,
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_payment(self, val_id):
        """
        Validate payment after completion
        """
        validation_url = f"{self.validation_url}?val_id={val_id}&store_id={self.store_id}&store_passwd={self.store_passwd}&format=json"
        
        try:
            response = requests.get(validation_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}