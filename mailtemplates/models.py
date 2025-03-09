from tenants.managers import TenantManager 
from django.db import models
from django.apps import apps  # ✅ Lazy import
from django.utils.translation import gettext_lazy as _

class EmailTemplate(models.Model):
    client = models.ForeignKey('tenants.Client', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_("Template Name"))
    sender = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Sender"))  # ✅ New Sender field
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))  # Email subject
    body = models.TextField(verbose_name=_("Body"))  # ✅ Use a simple TextField instead

    objects = TenantManager()

    def __str__(self):
        return self.name


