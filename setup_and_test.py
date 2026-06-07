# setup_and_test.py
import os
import sys
import subprocess

def check_system():
    """Check if system is ready"""
    print("🔍 Checking bKash Payment System Setup...")
    print("=" * 60)
    
    # Check required directories
    required_dirs = [
        'templates/payments',
        'payments',
        'orders',
    ]
    
    print("\n📁 Directory Check:")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   ❌ {directory}/ - Create this directory")
    
    # Check required files
    required_files = [
        'templates/payments/payment_methods.html',
        'templates/payments/order_complete.html',
        'templates/payments/payment_failed.html',
        'payments/views.py',
        'payments/urls.py',
        'payments/sslcommerz_service.py',
        'orders/views.py',
        'orders/urls.py',
    ]
    
    print("\n📄 File Check:")
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
    
    # Check if templates have content
    print("\n📝 Template Content Check:")
    template_files = [
        'templates/payments/payment_methods.html',
        'templates/payments/order_complete.html',
    ]
    
    for template in template_files:
        if os.path.exists(template):
            with open(template, 'r') as f:
                content = f.read()
                if len(content.strip()) > 100:
                    print(f"   ✅ {template} has content")
                else:
                    print(f"   ⚠️  {template} might be empty")
        else:
            print(f"   ❌ {template} not found")
    
    print("\n" + "=" * 60)
    print("SETUP CHECK COMPLETE!")
    print("=" * 60)

def run_server():
    """Start the Django server"""
    print("\n🚀 Starting Django Server...")
    print("=" * 60)
    
    try:
        # Run migrations
        print("\n1. Running migrations...")
        subprocess.run(['python', 'manage.py', 'makemigrations'], check=True)
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)
        
        # Create superuser if needed
        print("\n2. Checking admin user...")
        create_admin = input("Create superuser? (y/n): ").lower()
        if create_admin == 'y':
            subprocess.run(['python', 'manage.py', 'createsuperuser'], check=True)
        
        # Start server
        print("\n3. Starting server...")
        print("\n✅ Server is starting on http://localhost:8000")
        print("📋 Test the bKash flow:")
        print("   1. http://localhost:8000/store/")
        print("   2. Add product to cart")
        print("   3. Checkout → Place Order")
        print("   4. Pay with bKash → SSLCommerz")
        print("\n⚠️  Press CTRL+C to stop the server")
        
        subprocess.run(['python', 'manage.py', 'runserver'])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def quick_test():
    """Run quick tests"""
    print("\n🧪 Running Quick Tests...")
    print("=" * 60)
    
    try:
        import django
        django.setup()
        
        from orders.models import Order
        from django.contrib.auth.models import User
        
        # Check database
        user_count = User.objects.count()
        order_count = Order.objects.count()
        
        print(f"\n📊 Database Status:")
        print(f"   Users: {user_count}")
        print(f"   Orders: {order_count}")
        
        if order_count > 0:
            order = Order.objects.first()
            print(f"\n📦 Sample Order:")
            print(f"   Number: {order.order_number}")
            print(f"   Total: £{order.order_total}")
            print(f"   Status: {'Paid' if order.is_ordered else 'Pending'}")
        
        # Test URLs
        print(f"\n🔗 Testing URL Access:")
        from django.test import Client
        client = Client()
        
        if order_count > 0:
            order = Order.objects.first()
            response = client.get(f'/payments/{order.order_number}/', follow=True)
            print(f"   Payment page: {'✅ Accessible' if response.status_code == 200 else '❌ Not accessible'}")
        
        print("\n✅ Quick tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")

def main():
    """Main menu"""
    print("=" * 60)
    print("bKash Payment System - Setup & Testing")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Check System Setup")
        print("2. Run Quick Tests")
        print("3. Start Server")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            check_system()
        elif choice == '2':
            quick_test()
        elif choice == '3':
            run_server()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == '__main__':
    main()