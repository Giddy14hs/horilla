#!/usr/bin/env python
"""
Database Reset Script for Horilla Employee Portal
This script will completely reset the database and create fresh migrations.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection

def reset_database():
    """Reset the database completely"""
    print("🔄 Starting database reset process...")
    
    # Step 1: Drop all tables
    print("📋 Dropping all existing tables...")
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Drop all tables
        for table in tables:
            if table != 'django_migrations':
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                print(f"   Dropped table: {table}")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    print("✅ All tables dropped successfully!")
    
    # Step 2: Remove all migration files (except __init__.py)
    print("🗑️  Removing old migration files...")
    migration_dirs = [
        'base/migrations/',
        'employee/migrations/',
        'attendance/migrations/',
        'leave/migrations/',
        'project/migrations/',
        'helpdesk/migrations/',
        'notifications/migrations/',
        'offboarding/migrations/',
        'biometric/migrations/',
        'facedetection/migrations/',
        'geofencing/migrations/',
        'horilla_audit/migrations/',
        'horilla_automations/migrations/',
        'horilla_backup/migrations/',
        'horilla_documents/migrations/',
        'horilla_views/migrations/',
    ]
    
    for migration_dir in migration_dirs:
        if os.path.exists(migration_dir):
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(migration_dir, file)
                    os.remove(file_path)
                    print(f"   Removed: {file_path}")
    
    print("✅ Old migration files removed!")
    
    # Step 3: Create fresh migrations
    print("📝 Creating fresh migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ Fresh migrations created!")
    except Exception as e:
        print(f"❌ Error creating migrations: {e}")
        return False
    
    # Step 4: Apply migrations to clean database
    print("🚀 Applying migrations to clean database...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations applied successfully!")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return False
    
    print("🎉 Database reset completed successfully!")
    print("📋 Next steps:")
    print("   1. Create a superuser: python manage.py createsuperuser")
    print("   2. Start the server: python manage.py runserver 8080")
    print("   3. Access your application at http://127.0.0.1:8080")
    
    return True

if __name__ == "__main__":
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
    django.setup()
    
    # Run the reset
    success = reset_database()
    if success:
        print("\n🎯 Database reset completed! Your application is ready for fresh data.")
    else:
        print("\n💥 Database reset failed. Please check the errors above.")
        sys.exit(1)

