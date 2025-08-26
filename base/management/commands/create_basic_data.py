from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.models import EmployeeShift, WorkType, Company
from leave.models import LeaveType
from employee.models import Employee


class Command(BaseCommand):
    help = 'Create basic data for shifts, work types, and leave types if none exist'

    def handle(self, *args, **options):
        # Get or create a default company
        company, created = Company.objects.get_or_create(
            company="Default Company",
            defaults={
                "address": "Default Address",
                "country": "Default Country",
                "state": "Default State",
                "city": "Default City",
                "zip": "00000"
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created company: {company.company}'))
        
        # Create basic shifts if none exist
        if not EmployeeShift.objects.exists():
            shifts_data = [
                "Morning Shift (9 AM - 5 PM)",
                "Afternoon Shift (2 PM - 10 PM)",
                "Night Shift (10 PM - 6 AM)",
                "Flexible Hours",
                "Remote Work"
            ]
            
            for shift_name in shifts_data:
                shift = EmployeeShift.objects.create(employee_shift=shift_name)
                shift.company_id.add(company)
                self.stdout.write(self.style.SUCCESS(f'Created shift: {shift.employee_shift}'))
        else:
            self.stdout.write(self.style.WARNING('Shifts already exist, skipping...'))
        
        # Create basic work types if none exist
        if not WorkType.objects.exists():
            work_types_data = [
                "Full Time",
                "Part Time",
                "Contract",
                "Internship",
                "Remote"
            ]
            
            for work_type_name in work_types_data:
                work_type = WorkType.objects.create(work_type=work_type_name)
                work_type.company_id.add(company)
                self.stdout.write(self.style.SUCCESS(f'Created work type: {work_type.work_type}'))
        else:
            self.stdout.write(self.style.WARNING('Work types already exist, skipping...'))
        
        # Create basic leave types if none exist
        if not LeaveType.objects.exists():
            leave_types_data = [
                ("Annual Leave", "paid"),
                ("Sick Leave", "paid"),
                ("Personal Leave", "unpaid"),
                ("Maternity Leave", "paid"),
                ("Paternity Leave", "paid"),
                ("Bereavement Leave", "paid"),
                ("Study Leave", "unpaid")
            ]
            
            for leave_name, payment in leave_types_data:
                leave_type = LeaveType.objects.create(
                    name=leave_name,
                    payment=payment,
                    company_id=company
                )
                self.stdout.write(self.style.SUCCESS(f'Created leave type: {leave_type.name}'))
        else:
            self.stdout.write(self.style.WARNING('Leave types already exist, skipping...'))
        
        self.stdout.write(self.style.SUCCESS('Basic data creation completed!'))
