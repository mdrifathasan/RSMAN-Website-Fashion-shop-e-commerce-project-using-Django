import re 
 
with open('greatkart/settings.py', 'r') as f: 
    content = f.read() 
 
print('=== Checking orders app ===') 
print('orders in file:', 'orders' in content) 
 
# Check if in INSTALLED_APPS 
match = re.search(r'INSTALLED_APPS\s*=\s*\[(.*?)\]', content, re.DOTALL) 
if match: 
    apps = match.group(1) 
    print('orders in INSTALLED_APPS:', "'orders'" in apps or '"orders"' in apps) 
    if "'orders'" not in apps and '"orders"' not in apps: 
        print('ERROR: orders NOT in INSTALLED_APPS!') 
else: 
    print('Could not find INSTALLED_APPS section') 
