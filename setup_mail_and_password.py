#!/usr/bin/env python
"""
Standalone script to configure mail server and reset passwords in Horilla.
This script can be run independently to set up email configuration and reset user passwords.
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

from django.contrib.auth.models import User
from base.models import DynamicEmailConfiguration


def configure_mail_server(host, port, username, password, from_email, display_name=None, 
                         use_tls=True, use_ssl=False, timeout=30, is_primary=True):
    """
    Configure mail server settings programmatically.
    
    Args:
        host (str): SMTP host (e.g., smtp.gmail.com)
        port (int): SMTP port (e.g., 587)
        username (str): Email username
        password (str): Email password
        from_email (str): Default from email
        display_name (str): Display name for emails
        use_tls (bool): Use TLS encryption
        use_ssl (bool): Use SSL encryption
        timeout (int): Email timeout in seconds
        is_primary (bool): Set as primary mail server
    """
    try:
        # Clear existing primary mail servers if setting a new one
        if is_primary:
            DynamicEmailConfiguration.objects.filter(is_primary=True).update(is_primary=False)
        
        # Create or update mail server configuration
        mail_config, created = DynamicEmailConfiguration.objects.get_or_create(
            host=host,
            port=port,
            defaults={
                'username': username,
                'password': password,
                'from_email': from_email,
                'display_name': display_name or username,
                'use_tls': use_tls,
                'use_ssl': use_ssl,
                'timeout': timeout,
                'is_primary': is_primary,
            }
        )
        
        if not created:
            # Update existing configuration
            mail_config.username = username
            mail_config.password = password
            mail_config.from_email = from_email
            mail_config.display_name = display_name or username
            mail_config.use_tls = use_tls
            mail_config.use_ssl = use_ssl
            mail_config.timeout = timeout
            mail_config.is_primary = is_primary
            mail_config.save()
        
        action = "created" if created else "updated"
        print(f"✓ Mail server configuration {action} successfully for {host}")
        
        if is_primary:
            print("✓ Mail server set as primary")
            
        return True
        
    except Exception as e:
        print(f"✗ Error configuring mail server: {e}")
        return False


def reset_user_password(username, new_password, email=None):
    """
    Reset a user's password programmatically.
    
    Args:
        username (str): Username of the user
        new_password (str): New password
        email (str): Email address (if creating new user)
    """
    try:
        # Try to find existing user
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        
        print(f"✓ Password reset successfully for user '{username}'")
        return True
        
    except User.DoesNotExist:
        if email:
            # Create new user if email is provided
            user = User.objects.create_user(
                username=username,
                email=email,
                password=new_password
            )
            print(f"✓ User '{username}' created successfully with the provided password")
            return True
        else:
            print(f"✗ User '{username}' does not exist. Provide email to create a new user.")
            return False
    
    except Exception as e:
        print(f"✗ Error resetting password: {e}")
        return False


def configure_gmail():
    """Configure Gmail SMTP settings."""
    print("\n=== Configuring Gmail SMTP ===")
    print("Note: You'll need to use an App Password, not your regular Gmail password.")
    print("To generate an App Password:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-Step Verification if not already enabled")
    print("3. Go to Security > App passwords")
    print("4. Generate a new app password for 'Mail'")
    print()
    
    username = input("Enter your Gmail address: ")
    password = input("Enter your Gmail App Password: ")
    display_name = input("Enter display name (optional): ") or username
    
    return configure_mail_server(
        host="smtp.gmail.com",
        port=587,
        username=username,
        password=password,
        from_email=username,
        display_name=display_name,
        use_tls=True,
        use_ssl=False,
        is_primary=True
    )


def configure_outlook():
    """Configure Outlook/Hotmail SMTP settings."""
    print("\n=== Configuring Outlook/Hotmail SMTP ===")
    
    username = input("Enter your Outlook email address: ")
    password = input("Enter your Outlook password: ")
    display_name = input("Enter display name (optional): ") or username
    
    return configure_mail_server(
        host="smtp-mail.outlook.com",
        port=587,
        username=username,
        password=password,
        from_email=username,
        display_name=display_name,
        use_tls=True,
        use_ssl=False,
        is_primary=True
    )


def configure_custom_smtp():
    """Configure custom SMTP settings."""
    print("\n=== Configuring Custom SMTP ===")
    
    host = input("Enter SMTP host (e.g., smtp.yourdomain.com): ")
    port = int(input("Enter SMTP port (e.g., 587): "))
    username = input("Enter email username: ")
    password = input("Enter email password: ")
    from_email = input("Enter from email address: ")
    display_name = input("Enter display name (optional): ") or username
    
    use_tls = input("Use TLS? (y/n, default: y): ").lower() != 'n'
    use_ssl = input("Use SSL? (y/n, default: n): ").lower() == 'y'
    
    return configure_mail_server(
        host=host,
        port=port,
        username=username,
        password=password,
        from_email=from_email,
        display_name=display_name,
        use_tls=use_tls,
        use_ssl=use_ssl,
        is_primary=True
    )


def main():
    """Main function to run the setup."""
    print("=== Horilla Mail Server and Password Setup ===")
    print()
    
    # Check if mail server is already configured
    existing_config = DynamicEmailConfiguration.objects.filter(is_primary=True).first()
    if existing_config:
        print(f"⚠️  Primary mail server already configured: {existing_config.host}")
        response = input("Do you want to reconfigure? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Mail server configuration
    print("\n1. Configure Mail Server")
    print("2. Reset User Password")
    print("3. Both")
    choice = input("Choose an option (1-3): ")
    
    if choice in ['1', '3']:
        print("\nSelect email provider:")
        print("1. Gmail")
        print("2. Outlook/Hotmail")
        print("3. Custom SMTP")
        
        provider_choice = input("Choose provider (1-3): ")
        
        success = False
        if provider_choice == '1':
            success = configure_gmail()
        elif provider_choice == '2':
            success = configure_outlook()
        elif provider_choice == '3':
            success = configure_custom_smtp()
        else:
            print("Invalid choice.")
            return
        
        if not success:
            print("Mail server configuration failed.")
            return
    
    if choice in ['2', '3']:
        print("\n2. Reset User Password")
        username = input("Enter username: ")
        new_password = input("Enter new password: ")
        email = input("Enter email (if creating new user, optional): ") or None
        
        if not reset_user_password(username, new_password, email):
            print("Password reset failed.")
            return
    
    print("\n✓ Setup completed successfully!")
    print("\nYou can now use the password reset functionality in your Horilla application.")


if __name__ == "__main__":
    main() 