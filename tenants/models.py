from django.db import models
from django.contrib.auth.models import Group
from django.apps import apps  # ✅ Lazy import
from django.utils.translation import gettext_lazy as _


##def get_attachment_model():
##    return apps.get_model('mailtemplates', 'Attachment')


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(unique=True)  # Unique identifier (could be a subdomain)
    contact_name = models.CharField(max_length=255, verbose_name=_("Name"))
    contact_email = models.CharField(max_length=255, verbose_name=_("Email"))
    contact_phone = models.CharField(max_length=50,verbose_name=_("Phone"))
    contact_plan = models.CharField(max_length=150,verbose_name=_("Plan"))
    contact_payment_date = models.CharField(max_length=30, verbose_name=_("Payment Date"))

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



class Attachment(models.Model):
    ###A custom attachment model to store file uploads.
    file = models.FileField(upload_to="uploads/")  # Stores files in /media/uploads/
    name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unnamed Attachment"

"""
class TenantAttachment(models.Model):
    ##Associates an Attachment with a Client,
    ##so that each client can define or manage their own attachments.
    ##attachment = models.FileField(upload_to="uploads/")  ##Circular reference
    #attachment = models.ForeignKey('mailtemplates.Attachment', on_delete=models.CASCADE, related_name='tenant_attachment_set') ##New line circular ref.
    ##client = models.ForeignKey(Client, on_delete=models.CASCADE)
    attachment = models.ForeignKey(
        'mailtemplates.Attachment',  # Use string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='tenant_attachments'
    )

    client = models.ForeignKey('tenants.Client', on_delete=models.CASCADE)
    #description = CKEditor5Field(blank=True, null=True)
    description = models.TextField() 

    def __str__(self):
        desc_part = f" - {self.description[:30]}..." if self.description else ""
        return f"{self.attachment.name} ({self.client.name}){desc_part}"
"""