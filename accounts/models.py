from tenants.managers import TenantManager 
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import apps  # ✅ Lazy import
from django.utils.translation import gettext_lazy as _



class CustomUser(AbstractUser):
    #client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)
    #client = models.ForeignKey(Client, on_delete=models.CASCADE)
    client = models.ForeignKey('tenants.Client', on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Department"))
    extension = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Extension"))
    user_group = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Group"))  # Custom field for grouping
    
    objects = TenantManager()

    def __str__(self):
        return self.username
