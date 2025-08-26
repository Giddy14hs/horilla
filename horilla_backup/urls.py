from django.urls import path
from . import views

urlpatterns = [
    # Local backup URLs are commented out in views.py, so removing them from here
    # path("local/", views.local_setup, name="local"),
    # path("local-start-stop/", views.local_Backup_stop_or_start, name="local_start_stop"),
    # path("local-delete/", views.local_Backup_delete, name="local_delete"),
    
    # Google Drive backup URLs
    path("gdrive/", views.gdrive_setup, name="gdrive"),
    path("gdrive-start-stop/", views.gdrive_Backup_stop_or_start, name="gdrive_start_stop"),
    path("gdrive-delete/", views.gdrive_Backup_delete, name="gdrive_delete"),
    path("gdrive-instant-backup/", views.gdrive_instant_backup, name="gdrive_instant_backup"),
]
