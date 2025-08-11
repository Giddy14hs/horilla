# Horilla Mail Server Configuration and Password Reset

This guide provides multiple ways to configure the mail server and reset passwords in your Horilla application without using the user interface.

## Problem
The primary mail server is not configured, which prevents password reset functionality from working.

## Solutions

### Option 1: Using Django Management Commands

#### Configure Mail Server
```bash
# Configure Gmail
python manage.py configure_mail_server --provider gmail --username your-email@gmail.com --password your-app-password --from_email your-email@gmail.com --is_primary

# Configure Outlook
python manage.py configure_mail_server --provider outlook --username your-email@outlook.com --password your-password --from_email your-email@outlook.com --is_primary

# Configure Custom SMTP
python manage.py configure_mail_server --host smtp.yourdomain.com --port 587 --username your-username --password your-password --from_email your-email@yourdomain.com --use_tls --is_primary
```

#### Reset User Password
```bash
# Reset existing user password
python manage.py reset_user_password --username your-username --password new-password

# Create new user with password
python manage.py reset_user_password --username new-user --password new-password --email user@example.com
```

### Option 2: Using the Interactive Setup Script

Run the interactive setup script:
```bash
python setup_mail_and_password.py
```

This script will guide you through:
1. Choosing an email provider (Gmail, Outlook, or Custom SMTP)
2. Entering your email credentials
3. Resetting user passwords

### Option 3: Using the Quick Setup Script

Edit `quick_setup.py` and uncomment/modify the configuration lines:

```python
# Configure Gmail
quick_configure_gmail('your-email@gmail.com', 'your-app-password')

# Configure Outlook
quick_configure_outlook('your-email@outlook.com', 'your-password')

# Reset password
quick_reset_password('username', 'new-password')
```

Then run:
```bash
python quick_setup.py
```

### Option 4: Direct Database Configuration

If you have database access, you can directly configure the mail server:

```python
from base.models import DynamicEmailConfiguration

# Clear existing primary configurations
DynamicEmailConfiguration.objects.filter(is_primary=True).update(is_primary=False)

# Create new Gmail configuration
mail_config = DynamicEmailConfiguration.objects.create(
    host="smtp.gmail.com",
    port=587,
    username="your-email@gmail.com",
    password="your-app-password",
    from_email="your-email@gmail.com",
    display_name="Your Name",
    use_tls=True,
    use_ssl=False,
    timeout=30,
    is_primary=True,
)
```

## Email Provider Configurations

### Gmail
- **Host**: `smtp.gmail.com`
- **Port**: `587`
- **TLS**: Yes
- **SSL**: No
- **Note**: You need to use an App Password, not your regular Gmail password

### Outlook/Hotmail
- **Host**: `smtp-mail.outlook.com`
- **Port**: `587`
- **TLS**: Yes
- **SSL**: No

### Office 365
- **Host**: `smtp.office365.com`
- **Port**: `587`
- **TLS**: Yes
- **SSL**: No

## Gmail App Password Setup

If using Gmail, you need to generate an App Password:

1. Go to your Google Account settings
2. Enable 2-Step Verification if not already enabled
3. Go to Security > App passwords
4. Generate a new app password for 'Mail'
5. Use this app password instead of your regular Gmail password

## Testing the Configuration

After configuring the mail server:

1. **Test the email configuration** using the test email feature in the admin interface
2. **Try the password reset functionality**:
   - Go to `/forgot-password`
   - Enter your username (not email)
   - Check your email for the reset link

## Troubleshooting

### Common Issues

1. **"Primary mail server is not configured"**
   - Make sure you set `is_primary=True` when creating the configuration
   - Check that the configuration was saved successfully

2. **Email not sending**
   - Verify your email credentials
   - Check if your email provider requires app passwords
   - Ensure the correct port and encryption settings

3. **User not found**
   - The system uses username, not email for password reset
   - Make sure the user exists in the database

### Verification Commands

Check if mail server is configured:
```python
from base.models import DynamicEmailConfiguration
config = DynamicEmailConfiguration.objects.filter(is_primary=True).first()
if config:
    print(f"Primary mail server: {config.host}")
else:
    print("No primary mail server configured")
```

Check if user exists:
```python
from django.contrib.auth.models import User
user = User.objects.filter(username='your-username').first()
if user:
    print(f"User found: {user.username}")
else:
    print("User not found")
```

## Security Notes

- Store email passwords securely
- Use app passwords for Gmail instead of regular passwords
- Consider using environment variables for sensitive credentials
- Regularly update email passwords

## Next Steps

After configuring the mail server:

1. Test the password reset functionality
2. Configure additional email templates if needed
3. Set up email notifications for other features
4. Monitor email sending logs for any issues

The mail server configuration will enable all email-related features in your Horilla application, including password reset, notifications, and automated emails. 