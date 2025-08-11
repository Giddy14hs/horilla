"""
Horilla management command to configure mail server settings.
"""

from django.core.management.base import BaseCommand, CommandError
from base.models import DynamicEmailConfiguration


class Command(BaseCommand):
    """
    Horilla management command to configure mail server settings.
    """

    help = "Configures mail server settings for Horilla"

    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, help="Email host (e.g., smtp.gmail.com)")
        parser.add_argument("--port", type=int, help="Email port (e.g., 587)")
        parser.add_argument("--username", type=str, help="Email username")
        parser.add_argument("--password", type=str, help="Email password")
        parser.add_argument("--from_email", type=str, help="Default from email")
        parser.add_argument("--display_name", type=str, help="Display name")
        parser.add_argument("--use_tls", action="store_true", help="Use TLS")
        parser.add_argument("--use_ssl", action="store_true", help="Use SSL")
        parser.add_argument("--timeout", type=int, default=30, help="Email timeout in seconds")
        parser.add_argument("--is_primary", action="store_true", help="Set as primary mail server")
        parser.add_argument("--provider", type=str, choices=["gmail", "outlook", "office365", "custom"], 
                          help="Pre-configured email provider")

    def handle(self, *args, **options):
        # Clear existing primary mail servers if setting a new one
        if options.get("is_primary"):
            DynamicEmailConfiguration.objects.filter(is_primary=True).update(is_primary=False)
        
        # Handle pre-configured providers
        if options.get("provider"):
            config = self.get_provider_config(options["provider"])
            if not config:
                raise CommandError(f"Unknown provider: {options['provider']}")
            
            # Override with any specific options provided
            for key, value in options.items():
                if value is not None and key != "provider":
                    config[key] = value
        else:
            # Use individual parameters
            config = {
                "host": options.get("host"),
                "port": options.get("port"),
                "username": options.get("username"),
                "password": options.get("password"),
                "from_email": options.get("from_email"),
                "display_name": options.get("display_name"),
                "use_tls": options.get("use_tls", True),
                "use_ssl": options.get("use_ssl", False),
                "timeout": options.get("timeout", 30),
                "is_primary": options.get("is_primary", True),
            }

        # Validate required fields
        required_fields = ["host", "port", "username", "password", "from_email"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise CommandError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            # Create or update the mail server configuration
            mail_config, created = DynamicEmailConfiguration.objects.get_or_create(
                host=config["host"],
                port=config["port"],
                defaults=config
            )
            
            if not created:
                # Update existing configuration
                for key, value in config.items():
                    setattr(mail_config, key, value)
                mail_config.save()

            action = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f'Mail server configuration {action} successfully for {config["host"]}'
                )
            )
            
            if config.get("is_primary"):
                self.stdout.write(
                    self.style.SUCCESS("Mail server set as primary")
                )

        except Exception as e:
            raise CommandError(f"Error configuring mail server: {e}")

    def get_provider_config(self, provider):
        """Get pre-configured settings for common email providers."""
        configs = {
            "gmail": {
                "host": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "use_ssl": False,
                "timeout": 30,
            },
            "outlook": {
                "host": "smtp-mail.outlook.com",
                "port": 587,
                "use_tls": True,
                "use_ssl": False,
                "timeout": 30,
            },
            "office365": {
                "host": "smtp.office365.com",
                "port": 587,
                "use_tls": True,
                "use_ssl": False,
                "timeout": 30,
            },
        }
        return configs.get(provider) 