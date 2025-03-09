

from django import forms

class TenantAdminMixin:
    """
    Mixin for ModelAdmin classes to enforce tenant assignment.
    For non-superadmin users (i.e. request.user.client.pk != 1), the 'client' field is removed.
    """
    def get_form(self, request, obj=None, **kwargs):
        #print("TenantAdminMixin get_form called. User client:", request.user.client)
        form = super().get_form(request, obj, **kwargs)
        
        if 'client' in form.base_fields and request.user.client.pk != 1:
            # Option 1: Remove the field entirely so it doesn't show up
            del form.base_fields['client']
            # Option 2 (if you prefer to keep it hidden): Uncomment the next two lines
            # form.base_fields['client'].widget = forms.HiddenInput()
            # form.base_fields['client'].initial = request.user.client.pk
        return form

    def save_model(self, request, obj, form, change):
        # Ensure that non-superadmin users have their client field automatically set
        if request.user.client.pk != 1:
            obj.client = request.user.client
        super().save_model(request, obj, form, change)
