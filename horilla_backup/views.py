from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from horilla.decorators import (
    hx_request_required,
    login_required,
    manager_can_enter,
    owner_can_enter,
    permission_required,
)

from .forms import *
from .gdrive import *
from .pgdump import *
from .scheduler import *
from .zip import *

# @login_required
# @permission_required("backup.add_localbackup")
# def local_setup(request):
#     """
#     function used to setup local backup.

#     Parameters:
#     request (HttpRequest): The HTTP request object.

#     Returns:
#     GET : return local backup setup template
#     POST : return settings
#     """
#     form = LocalBackupSetupForm()
#     show = False
#     active = False
#     if LocalBackup.objects.exists():
#         form = LocalBackupSetupForm(instance=LocalBackup.objects.first())
#         show = True
#         active = LocalBackup.objects.first().active
#     if request.method == "POST":
#         form = LocalBackupSetupForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             stop_backup_job()
#             messages.success(request, _("Local backup automation setup updated."))
#             return redirect("local")
#     return render(request, "backup/local_setup_form.html", {"form": form, "show":show, "active":active})


# @login_required
# @permission_required("backup.change_localbackup")
# def local_Backup_stop_or_start(request):
#     """
#     function used to stop or start local backup.

#     Parameters:
#     request (HttpRequest): The HTTP request object.

#     Returns:
#     GET : return local backup setup template
#     POST : return settings
#     """
#     if LocalBackup.objects.exists():
#         local_backup = LocalBackup.objects.first()
#         if local_backup.active == True:
#             local_backup.active = False
#             stop_backup_job()
#             message = "Local Backup Automation Stopped Successfully."
#         else:
#             local_backup.active = True
#             start_backup_job()
#             message = "Local Backup Automation Started Successfully."
#         local_backup.save()
#         messages.success(request, _(message))
#     return redirect("local")


# @login_required
# @permission_required("backup.delete_localbackup")
# def local_Backup_delete(request):
#     """
#     function used to delete local backup.

#     Parameters:
#     request (HttpRequest): The HTTP request object.

#     Returns:
#     GET : return local backup setup template
#     POST : return settings
#     """
#     if LocalBackup.objects.exists():
#         local_backup = LocalBackup.objects.first()
#         local_backup.delete()
#         stop_backup_job()
#         messages.success(request, _("Local Backup Automation Removed Successfully."))
#     return redirect("local")


@login_required
@permission_required("backup.add_localbackup")
def gdrive_setup(request):
    """
    function used to setup gdrive backup.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    GET : return gdrive backup setup template
    POST : return gdrive backup update template
    """
    form = GdriveBackupSetupForm()
    show = False
    active = False
    db_vendor = connection.vendor
    
    # Check if database is supported for automated backup
    automated_backup_supported = db_vendor == "postgresql"
    
    if GoogleDriveBackup.objects.exists():
        instance = GoogleDriveBackup.objects.first()
        form = GdriveBackupSetupForm(instance=instance)
        show = True
        active = GoogleDriveBackup.objects.first().active
        if request.method == "POST":
            form = GdriveBackupSetupForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                google_drive = form.save()
                # Only allow active state for PostgreSQL databases
                if not automated_backup_supported:
                    google_drive.active = False
                google_drive.save()
                if automated_backup_supported:
                    stop_gdrive_backup_job()
                messages.success(request, _("gdrive backup automation setup updated."))
                return redirect("gdrive")
        return render(
            request,
            "backup/gdrive_setup_form.html",
            {
                "form": form, 
                "show": show, 
                "active": active, 
                "automated_backup_supported": automated_backup_supported,
                "db_vendor": db_vendor
            },
        )

    if request.method == "POST":
        form = GdriveBackupSetupForm(request.POST, request.FILES)
        if form.is_valid():
            google_drive = form.save()
            # Only allow active state for PostgreSQL databases
            if not automated_backup_supported:
                google_drive.active = False
            google_drive.save()
            messages.success(request, _("gdrive backup automation setup Created."))
            return redirect("gdrive")
    return render(
        request,
        "backup/gdrive_setup_form.html",
        {
            "form": form, 
            "show": show, 
            "active": active, 
            "automated_backup_supported": automated_backup_supported,
            "db_vendor": db_vendor
        },
    )


@login_required
@permission_required("backup.change_localbackup")
def gdrive_Backup_stop_or_start(request):
    """
    function used to stop or start gdrive backup.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    GET : return gdrive backup setup template
    POST : return gdrive backup update template
    """
    if GoogleDriveBackup.objects.exists():
        gdive_backup = GoogleDriveBackup.objects.first()
        if gdive_backup.active == True:
            gdive_backup.active = False
            stop_gdrive_backup_job()
            message = "Gdrive Backup Automation Stopped Successfully."
        else:
            gdive_backup.active = True
            start_gdrive_backup_job()
            message = "Gdrive Backup Automation Started Successfully."
        gdive_backup.save()
        messages.success(request, _(message))
    return redirect("gdrive")


@login_required
@permission_required("backup.delete_localbackup")
def gdrive_Backup_delete(request):
    """
    function used to delete gdrive backup.

        Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    GET : return gdrive backup setup template
    """
    if GoogleDriveBackup.objects.exists():
        gdrive_backup = GoogleDriveBackup.objects.first()
        gdrive_backup.delete()
        stop_gdrive_backup_job()
        messages.success(request, _("Gdrive Backup Automation Removed Successfully."))
    return redirect("gdrive")


@login_required
@permission_required("backup.add_localbackup")
def gdrive_instant_backup(request):
    """
    function used to create instant backup and download as SQL file.
    
    Parameters:
    request (HttpRequest): The HTTP request object.
    
    Returns:
    GET : return instant backup download
    """
    from django.http import HttpResponse
    from django.db import connection
    import tempfile
    import os
    from datetime import datetime
    
    # Check database type and provide appropriate backup
    db_vendor = connection.vendor
    
    if db_vendor == "postgresql":
        return _create_postgresql_backup(request)
    elif db_vendor == "sqlite3":
        return _create_sqlite_backup(request)
    elif db_vendor == "mysql":
        return _create_mysql_backup(request)
    else:
        messages.error(request, _("Instant backup is not supported for {db_type} databases.").format(db_type=db_vendor))
        return redirect("gdrive")


def _create_postgresql_backup(request):
    """Create PostgreSQL backup"""
    from django.http import HttpResponse
    from django.db import connection
    import tempfile
    import os
    from datetime import datetime
    
    try:
        # Create a temporary file for the backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Get database connection details
        db = connection.settings_dict
        db_name = db.get("NAME")
        username = db.get("USER")
        password = db.get("PASSWORD")
        host = db.get("HOST", "localhost")
        port = db.get("PORT", 5432)
        
        # Create SQL dump using pg_dump with SQL format
        from .pgdump import dump_postgres_db
        dump_postgres_db(
            db_name=db_name,
            username=username,
            output_file=temp_file_path,
            password=password,
            host=host,
            port=port,
            format="sql"  # Use SQL format for readable output
        )
        
        # Check if the backup file was created successfully
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
            raise Exception("Backup file was not created or is empty")
        
        # Read the backup file
        with open(temp_file_path, 'rb') as f:
            backup_data = f.read()
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Create HTTP response with the backup file
        filename = f"postgresql_backup_{timestamp}.sql"
        response = HttpResponse(backup_data, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(request, _("PostgreSQL backup created successfully!"))
        return response
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        messages.error(request, f"PostgreSQL backup failed: {str(e)}")
        return redirect("gdrive")


def _create_sqlite_backup(request):
    """Create SQLite backup"""
    from django.http import HttpResponse
    from django.db import connection
    import shutil
    from datetime import datetime
    
    try:
        # Get database file path
        db_path = connection.settings_dict.get("NAME")
        
        if not os.path.exists(db_path):
            raise Exception("SQLite database file not found")
        
        # Create a copy of the database file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sqlite_backup_{timestamp}.db"
        
        # Read the database file
        with open(db_path, 'rb') as f:
            backup_data = f.read()
        
        # Create HTTP response with the backup file
        response = HttpResponse(backup_data, content_type='application/x-sqlite3')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(request, _("SQLite backup created successfully!"))
        return response
        
    except Exception as e:
        messages.error(request, f"SQLite backup failed: {str(e)}")
        return redirect("gdrive")


def _create_mysql_backup(request):
    """Create MySQL backup"""
    from django.http import HttpResponse
    from django.db import connection
    import tempfile
    import os
    import subprocess
    from datetime import datetime
    
    try:
        # Create a temporary file for the backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Get database connection details
        db = connection.settings_dict
        db_name = db.get("NAME")
        username = db.get("USER")
        password = db.get("PASSWORD")
        host = db.get("HOST", "localhost")
        port = db.get("PORT", 3306)
        
        # Create MySQL dump using mysqldump
        dump_command = [
            "mysqldump",
            "-h", host,
            "-P", str(port),
            "-u", username,
            "--result-file=" + temp_file_path,
            db_name
        ]
        
        # Set password environment variable if provided
        env = os.environ.copy()
        if password:
            env["MYSQL_PWD"] = password
        
        # Execute mysqldump
        result = subprocess.run(
            dump_command, 
            env=env, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        # Check if the backup file was created successfully
        if not os.path.exists(temp_file_path) or os.path.getsize(temp_file_path) == 0:
            raise Exception("MySQL backup file was not created or is empty")
        
        # Read the backup file
        with open(temp_file_path, 'rb') as f:
            backup_data = f.read()
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Create HTTP response with the backup file
        filename = f"mysql_backup_{timestamp}.sql"
        response = HttpResponse(backup_data, content_type='application/sql')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        messages.success(request, _("MySQL backup created successfully!"))
        return response
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        messages.error(request, f"MySQL backup failed: {str(e)}")
        return redirect("gdrive")
