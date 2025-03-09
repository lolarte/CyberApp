from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group 
from .models import CustomUser
from core.admin_mixins import TenantAdminMixin

@admin.register(CustomUser)
class CustomUserAdmin(TenantAdminMixin, UserAdmin):
    list_display = ('username', 'email', 'client', 'is_staff', 'is_active')
    
    # Extend the default fieldsets to include your custom fields.
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department', 'extension', 'user_group')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('department', 'extension', 'user_group')}),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Return the fieldsets for the admin form.
        For superadmin users (client=1): ensure the client field is present.
        For non-superadmin users: remove the client field.
        """
        # Get the fieldsets as defined above.
        fieldsets = list(super().get_fieldsets(request, obj))
        
        if request.user.client.pk == 1:
            # Superadmin should see the client field.
            # Check if any fieldset already contains 'client'.
            found = any('client' in fs[1].get('fields', ()) for fs in fieldsets)
            if not found:
                # Add a new section with the client field.
                fieldsets.append(('Client Information', {'fields': ('client',)}))
        else:
            # For non-superadmin, remove the client field from all fieldsets.
            new_fieldsets = []
            for title, options in fieldsets:
                fields = list(options.get('fields', ()))
                if 'client' in fields:
                    fields.remove('client')
                new_fieldsets.append((title, {'fields': tuple(fields)}))
            fieldsets = new_fieldsets

        return tuple(fieldsets)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the logged-in user's client is not superadmin (client=1), filter by client.
        if request.user.client.pk != 1:
            qs = qs.filter(client=request.user.client)
        return qs

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        When editing or creating a user, filter the 'groups' field 
        to only include groups that match the current user's client 
        (unless user is superadmin).
        """
        if db_field.name == 'groups':
            if request.user.client.pk != 1:
                # Only show groups linked to the current user's client
                kwargs["queryset"] = Group.objects.filter(tenant_data__client=request.user.client)
        return super().formfield_for_manytomany(db_field, request, **kwargs)