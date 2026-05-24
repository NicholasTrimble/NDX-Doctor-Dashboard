import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory, Client
from doctors.views import main_dashboard

print("Testing dashboard view...")

# Method 1: Direct view call
factory = RequestFactory()
request = factory.get('/')

try:
    response = main_dashboard(request)
    print(f'Direct view call - Status: {response.status_code}')

    # Try to access context
    if hasattr(response, 'context') and response.context:
        context = response.context
        print("✓ Found context data")
        print(f'  Labels: {len(context.get("labels", []))} items')
        print(f'  Data points: {len(context.get("data", []))} items')
        print(f'  Action plan: {len(context.get("action_plan", []))} items')
        print(f'  Departments: {len(context.get("departments", []))} items')
    else:
        print("✗ No context data found")

except Exception as e:
    print(f'✗ Error in direct view call: {e}')

# Method 2: Client request
print("\nTesting with Django test client...")
client = Client()
try:
    response = client.get('/')
    print(f'Client request - Status: {response.status_code}')
    if response.status_code == 200:
        print("✓ Dashboard page loads successfully")
        # Check if it contains expected content
        if 'dashboard' in response.content.decode().lower():
            print("✓ Response contains dashboard content")
        else:
            print("✗ Response does not contain dashboard content")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f'✗ Error in client request: {e}')

print("\nDashboard test complete.")