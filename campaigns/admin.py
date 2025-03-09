print("campaigns/admin.py loaded")

from django.contrib import admin
from .models import Campaign, PhishingTestLog
from core.admin_mixins import TenantAdminMixin  # Confirm correct import


@admin.register(Campaign)
class CampaignAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'number_of_emails', 'created_at')
    search_fields = ('title',)
    filter_horizontal = ('groups', 'templates',)  # For easier selection in the admin

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # For superadmin (client=1), show all; for others, filter by their client.
        if request.user.client.pk != 1:
            qs = qs.filter(client=request.user.client)
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # When editing the "templates" field, filter by the current user's client.
        if db_field.name == "templates":
            if request.user.client.pk != 1:
                kwargs["queryset"] = db_field.related_model.objects.filter(client=request.user.client)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #print("CampaignAdmin initialized")
#admin.site.register(Campaign, CampaignAdmin)

@admin.register(PhishingTestLog)
class PhishingTestLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'action', 'timestamp')
    list_filter = ('action', 'campaign')
    search_fields = ('user__username',)
