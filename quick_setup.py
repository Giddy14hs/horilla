#!/usr/bin/env python
"""
Quick setup script for Horilla mail server configuration.
This script provides a simple way to configure the mail server without interactive prompts.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from base.models import DynamicEmailConfiguration
from django.contrib.auth.models import User


def quick_configure_gmail(email, app_password, display_name=None):
    """Quickly configure Gmail SMTP settings."""
    try:
        # Clear existing primary mail servers
        DynamicEmailConfiguration.objects.filter(is_primary=True).update(is_primary=False)
        
        # Create Gmail configuration
        mail_config = DynamicEmailConfiguration.objects.create(
            host="smtp.gmail.com",
            port=587,
            username=email,
            password=app_password,
            from_email=email,
            display_name=display_name or email,
            use_tls=True,
            use_ssl=False,
            timeout=30,
            is_primary=True,
        )
        
        print(f"✓ Gmail mail server configured successfully: {email}")
        return True
        
    except Exception as e:
        print(f"✗ Error configuring Gmail: {e}")
        return False


def quick_configure_outlook(email, password, display_name=None):
    """Quickly configure Outlook SMTP settings."""
    try:
        # Clear existing primary mail servers
        DynamicEmailConfiguration.objects.filter(is_primary=True).update(is_primary=False)
        
        # Create Outlook configuration
        mail_config = DynamicEmailConfiguration.objects.create(
            host="smtp-mail.outlook.com",
            port=587,
            username=email,
            password=password,
            from_email=email,
            display_name=display_name or email,
            use_tls=True,
            use_ssl=False,
            timeout=30,
            is_primary=True,
        )
        
        print(f"✓ Outlook mail server configured successfully: {email}")
        return True
        
    except Exception as e:
        print(f"✗ Error configuring Outlook: {e}")
        return False


def quick_reset_password(username, new_password):
    """Quickly reset a user's password."""
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        print(f"✓ Password reset successfully for user: {username}")
        return True
        
    except User.DoesNotExist:
        print(f"✗ User '{username}' does not exist")
        return False
    except Exception as e:
        print(f"✗ Error resetting password: {e}")
        return False


if __name__ == "__main__":
    print("=== Quick Horilla Setup ===")
    print()
    
    # Example usage - modify these values as needed
    print("To configure Gmail:")
    print("quick_configure_gmail('your-email@gmail.com', 'your-app-password')")
    print()
    print("To configure Outlook:")
    print("quick_configure_outlook('your-email@outlook.com', 'your-password')")
    print()
    print("To reset password:")
    print("quick_reset_password('username', 'new-password')")
    print()
    
    # Uncomment and modify the lines below to run automatically
    # Example: Configure Gmail
    # quick_configure_gmail('your-email@gmail.com', 'your-app-password')
    
    # Example: Reset password
    # quick_reset_password('admin', 'new-password')
    
    print("Edit this script to configure your mail server and reset passwords.") 