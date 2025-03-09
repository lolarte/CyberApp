import threading
from django.db import models
from django.contrib.auth.models import UserManager  # Import the default UserManager

# Thread-local storage to hold the current client (tenant)
_thread_locals = threading.local()

def get_current_client():
    return getattr(_thread_locals, 'client', None)

class TenantManager(UserManager):
    def get_queryset(self):
        client = get_current_client()
        if client:
            return super().get_queryset().filter(client=client)
        return super().get_queryset()
