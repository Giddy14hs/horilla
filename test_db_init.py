#!/usr/bin/env python3
"""
Simple script to test database initialization password
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

# Now we can import Django models and settings
from horilla.horilla_settings import DB_INIT_PASSWORD

print("Database Initialization Password:")
print(f"Password: {DB_INIT_PASSWORD}")
print(f"Length: {len(DB_INIT_PASSWORD)}")
print(f"Type: {type(DB_INIT_PASSWORD)}")

# Test if it's accessible from base.views
try:
    from base.views import DB_INIT_PASSWORD as imported_password
    print(f"\nSuccessfully imported from base.views: {imported_password}")
except ImportError as e:
    print(f"\nImport error from base.views: {e}")
except Exception as e:
    print(f"\nOther error: {e}")

print("\nTo use this password:")
print("1. Go to http://localhost:8000/initialize-database")
print("2. Enter the password shown above")
print("3. Follow the setup wizard")
