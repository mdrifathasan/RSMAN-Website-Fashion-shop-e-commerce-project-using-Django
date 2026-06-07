import re 
with open('greatkart/settings.py', 'r') as f: 
    content = f.read() 
if 'orders' in content: 
    print('û orders found in settings.py') 
    match = re.search(r'INSTALLED_APPS\s*=\s*\[(.*?)\]', content, re.DOTALL) 
    if match: 
        apps_section = match.group(1) 
        if "'orders'" in apps_section or '"orders"' in apps_section: 
            print('û orders is in INSTALLED_APPS') 
        else: 
            print('? orders is NOT in INSTALLED_APPS') 
else: 
