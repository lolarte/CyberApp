from tenants.managers import TenantManager 
from django.db import models
from django.conf import settings  # For referencing your CustomUser model
from django.contrib.auth.models import Group
from tenants.models import Client
from django.utils.translation import gettext_lazy as _


class Campaign(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Name"))
    # Removed: email_subject = models.CharField(max_length=255)
    # Removed: email_message = models.TextField()
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))
    number_of_emails = models.PositiveIntegerField(default=1, verbose_name=_("Number of Emails"))
    
    # New tenant field:
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    # New fields:
    groups = models.ManyToManyField(Group, blank=True)  # Target users must belong to these groups
    templates = models.ManyToManyField('mailtemplates.EmailTemplate', blank=True)  # Associated email templates
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

ACTION_CHOICES = (
    ('reported', 'Reported'),
    ('clicked', 'Clicked'),
)

class PhishingTestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.campaign.title} - {self.action}"
