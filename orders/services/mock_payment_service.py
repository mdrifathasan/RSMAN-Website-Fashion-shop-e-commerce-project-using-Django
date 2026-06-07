import random
import time
import logging

logger = logging.getLogger(__name__)

class MockBKashPayment:
    """Mock bKash service for testing"""
    
    def create_payment(self, amount, order_id, mobile_number):
        """Mock bKash payment creation"""
        logger.info(f"Mock bKash: Creating payment for order {order_id}")
        
        # Simulate API delay
        time.sleep(1)
        
        # Generate mock response
        mock_payment_id = f"BKASH_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return {
            'success': True,
            'payment_id': mock_payment_id,
            'bkash_url': f"mock://bkash.pay/{mock_payment_id}",
            'transaction_status': 'INITIATED',
            'message': 'Payment request sent to bKash app'
        }
    
    def verify_payment(self, payment_id):
        """Mock payment verification"""
        logger.info(f"Mock bKash: Verifying payment {payment_id}")
        time.sleep(0.5)
        
        # Simulate 80% success rate
        if random.random() > 0.2:
            return {
                'success': True,
                'status': 'COMPLETED',
                'transaction_id': f"TRX_{int(time.time())}",
                'message': 'Payment verified successfully'
            }
        else:
            return {
                'success': False,
                'status': 'FAILED',
                'message': 'Payment failed or cancelled'
            }


class MockNagadPayment:
    """Mock Nagad service for testing"""
    
    def create_payment(self, amount, order_id, mobile_number):
        """Mock Nagad payment creation"""
        logger.info(f"Mock Nagad: Creating payment for order {order_id}")
        
        # Simulate API delay
        time.sleep(1)
        
        # Generate mock response
        mock_payment_id = f"NAGAD_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return {
            'success': True,
            'payment_id': mock_payment_id,
            'callback_url': f"mock://nagad.callback/{mock_payment_id}",
            'message': 'Payment request sent to Nagad app'
        }
    
    def verify_payment(self, payment_id):
        """Mock payment verification"""
        logger.info(f"Mock Nagad: Verifying payment {payment_id}")
        time.sleep(0.5)
        
        # Simulate 80% success rate
        if random.random() > 0.2:
            return {
                'success': True,
                'status': 'SUCCESS',
                'transaction_id': f"TRX_{int(time.time())}",
                'message': 'Payment verified successfully'
            }
        else:
            return {
                'success': False,
                'status': 'FAILED',
                'message': 'Payment failed or cancelled'
            }