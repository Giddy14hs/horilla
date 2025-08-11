"""
Horilla management command to create users with different permission levels.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from employee.models import Employee


class Command(BaseCommand):
    """
    Horilla management command to create users with different permission levels.
    """

    help = "Creates a user with specific permission levels (admin, manager, employee)"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, required=True, help="Username for the new user")
        parser.add_argument("--email", type=str, required=True, help="Email for the new user")
        parser.add_argument("--password", type=str, required=True, help="Password for the new user")
        parser.add_argument("--first_name", type=str, required=True, help="First name")
        parser.add_argument("--last_name", type=str, required=True, help="Last name")
        parser.add_argument("--phone", type=str, help="Phone number")
        parser.add_argument("--user_type", type=str, choices=["admin", "manager", "employee"], 
                          default="employee", help="Type of user to create")
        parser.add_argument("--is_superuser", action="store_true", help="Make user a superuser (admin only)")
        parser.add_argument("--groups", nargs="+", help="Groups to assign to the user")
        parser.add_argument("--permissions", nargs="+", help="Specific permissions to assign")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]
        phone = options.get("phone", "")
        user_type = options["user_type"]
        is_superuser = options["is_superuser"]
        groups = options.get("groups", [])
        permissions = options.get("permissions", [])

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User with username "{username}" already exists')
            )
            return

        try:
            # Create user with appropriate settings
            if user_type == "admin":
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_superuser=is_superuser,
                    is_staff=True,
                )
                
                # Assign admin permissions
                admin_permissions = [
                    'add_employee', 'change_employee', 'delete_employee', 'view_employee',
                    'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance',
                    'add_leave', 'change_leave', 'delete_leave', 'view_leave',
                    'add_pms', 'change_pms', 'delete_pms', 'view_pms',
                    'add_user', 'change_user', 'delete_user', 'view_user',
                ]
                perms = Permission.objects.filter(codename__in=admin_permissions)
                user.user_permissions.set(perms)
                
            elif user_type == "manager":
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_superuser=False,
                    is_staff=True,
                )
                
                # Assign manager permissions (subset of admin permissions)
                manager_permissions = [
                    'view_employee', 'change_employee', 'add_employee',
                    'view_attendance', 'change_attendance',
                    'view_leave', 'change_leave',
                    'view_pms', 'change_pms',
                ]
                perms = Permission.objects.filter(codename__in=manager_permissions)
                user.user_permissions.set(perms)
                
            else:  # employee
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_superuser=False,
                    is_staff=False,
                )
                
                # Assign employee permissions
                employee_permissions = [
                    'view_ownprofile', 'change_ownprofile',
                    'view_attendance', 'add_attendance',
                    'view_leave', 'add_leave',
                ]
                perms = Permission.objects.filter(codename__in=employee_permissions)
                user.user_permissions.set(perms)

            # Assign specific groups if provided
            if groups:
                group_objects = Group.objects.filter(name__in=groups)
                user.groups.set(group_objects)
                self.stdout.write(f"Assigned groups: {', '.join(groups)}")

            # Assign specific permissions if provided
            if permissions:
                perm_objects = Permission.objects.filter(codename__in=permissions)
                user.user_permissions.add(*perm_objects)
                self.stdout.write(f"Assigned permissions: {', '.join(permissions)}")

            # Create employee record
            employee = Employee.objects.create(
                employee_user_id=user,
                employee_first_name=first_name,
                employee_last_name=last_name,
                email=email,
                phone=phone,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'{user_type.title()} "{username}" created successfully with appropriate permissions'
                )
            )
            
            # Display user information
            self.stdout.write(f"Username: {username}")
            self.stdout.write(f"Email: {email}")
            self.stdout.write(f"User Type: {user_type}")
            self.stdout.write(f"Superuser: {user.is_superuser}")
            self.stdout.write(f"Staff: {user.is_staff}")
            self.stdout.write(f"Active: {user.is_active}")

        except Exception as e:
            if "user" in locals():
                user.delete()
            raise CommandError(f'Error creating user "{username}": {e}') from e 