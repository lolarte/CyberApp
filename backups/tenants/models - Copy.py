from django.db import models
from django.contrib.auth.models import Group
from django_summernote.models import Attachment  # Import the built-in Attachment model from django-summernote

class Client(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)  # e.g., a unique identifier (could be subdomain)
    contact_name = models.CharField(max_length=255)
    contact_email = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=50)
    contact_plan = models.CharField(max_length=150)
    contact_payment_date = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class TenantGroup(models.Model):
    """
    Associates a Django auth Group with a Client,
    so that each client can define its own groups.
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='tenant_data'
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        desc_part = f" - {self.description[:30]}..." if self.description else ""
        return f"{self.group.name} ({self.client.name}){desc_part}"

class TenantAttachment(models.Model):
    """
    Associates a django-summernote Attachment with a Client,
    so that each client can define or manage their own attachments.
    """
    attachment = models.OneToOneField(
        Attachment,
        on_delete=models.CASCADE,
        related_name='tenant_data'
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        desc_part = f" - {self.description[:30]}..." if self.description else ""
        return f"{self.attachment.name} ({self.client.name}){desc_part}"
