"""
Horilla management command to reset a user's password.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Horilla management command to reset a user's password.
    """

    help = "Resets a user's password"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, required=True, help="Username of the user")
        parser.add_argument("--password", type=str, required=True, help="New password for the user")
        parser.add_argument("--email", type=str, help="Email of the user (if creating new user)")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options.get("email")

        try:
            # Try to find existing user
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Password reset successfully for user "{username}"')
            )
            
        except User.DoesNotExist:
            if email:
                # Create new user if email is provided
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'User "{username}" created successfully with the provided password')
                )
            else:
                raise CommandError(f'User "{username}" does not exist. Use --email to create a new user.')
        
        except Exception as e:
            raise CommandError(f"Error resetting password: {e}") 