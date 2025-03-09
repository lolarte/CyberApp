from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django_summernote.models import Attachment
from .models import Client, TenantGroup, TenantAttachment

# 1. Unregister the default Group admin if it's already registered
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

#Unregister default Attachment form
try:
    admin.site.unregister(Attachment)
except admin.sites.NotRegistered:
    pass

class TenantAdmin(admin.ModelAdmin):
    """
    Base admin class to automatically assign the current tenant (client)
    to tenant-specific objects on creation.
    """
    def save_model(self, request, obj, form, change):
        if not change and hasattr(request, 'client') and request.client:
            obj.client = request.client
        super().save_model(request, obj, form, change)


class GroupForm(forms.ModelForm):
    """
    Custom form for Django's built-in Group model.
    - superadmin (client=1) can select the client via a drop-down.
    - non-superadmin won't see the client field (auto-assigned).
    - 'description' is stored in TenantGroup, so we handle it separately from Group's fields.
    """
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Client (Superadmin Only)"
    )
    description = forms.CharField(
        label="Description (Tenant-Specific)",
        required=False,
        widget=forms.Textarea
    )

    class Meta:
        model = Group
        # Group doesn't have a 'description' field, so we exclude it from the model fields.
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # If editing an existing Group, load the associated TenantGroup data if it exists
        if self.instance and self.instance.pk:
            try:
                tenant_group = self.instance.tenant_data
                self.fields['client'].initial = tenant_group.client.pk
                self.fields['description'].initial = tenant_group.description
            except TenantGroup.DoesNotExist:
                pass

        # If the user is not superadmin, hide the 'client' field
        if self.request and self.request.user.client.pk != 1:
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = self.request.user.client.pk

    def save(self, commit=True):
        """
        1. Save the built-in Group (name, permissions).
        2. Create or update TenantGroup for 'client' and 'description'.
        """
        group = super().save(commit=commit)
        chosen_client = self.cleaned_data.get('client') or (
            self.request.user.client if self.request else None
        )
        if not chosen_client:
            # Default to client=1 if none is chosen and there's no user context
            chosen_client = Client.objects.get(pk=1)

        # Create or update the associated TenantGroup
        try:
            tenant_group = group.tenant_data
        except TenantGroup.DoesNotExist:
            tenant_group = None

        if not tenant_group:
            TenantGroup.objects.create(
                group=group,
                client=chosen_client,
                description=self.cleaned_data.get('description', '')
            )
        else:
            tenant_group.client = chosen_client
            tenant_group.description = self.cleaned_data.get('description', '')
            tenant_group.save()

        return group


class CustomGroupAdmin(admin.ModelAdmin):
    """
    Custom admin for the built-in Group model:
     - Non-superadmin sees only groups for their client, and can't change the client.
     - Superadmin can pick any client and set the tenant-specific description.
    """
    list_display = ('name', 'get_client', 'get_description')
    form = GroupForm

    def get_form(self, request, obj=None, **kwargs):
        """ 
        Pass `request` into GroupForm so we can hide/lock the client for non-superadmins.
        """
        kwargs['form'] = self.form
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs['request'] = request
                super().__init__(*args, **inner_kwargs)

        return FormWithRequest

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.client.pk != 1:
            qs = qs.filter(tenant_data__client=request.user.client)
        return qs

    def get_client(self, obj):
        """
        Display the associated client's name from TenantGroup.
        """
        return obj.tenant_data.client.name if hasattr(obj, 'tenant_data') else 'No TenantGroup'
    get_client.short_description = 'Client'

    def get_description(self, obj):
        """
        Display the associated TenantGroup's description.
        """
        return obj.tenant_data.description if hasattr(obj, 'tenant_data') else ''
    get_description.short_description = 'Description'

    def save_model(self, request, obj, form, change):
        """
        After saving the Group, rely on the form's save() to manage TenantGroup as well.
        """
        super().save_model(request, obj, form, change)

# 2. Register the custom Group admin to unify group management
admin.site.register(Group, CustomGroupAdmin)

#Custom attachments form associated with each client
class AttachmentForm(forms.ModelForm):
    """
    A custom form for django-summernote's Attachment model,
    associating it with TenantAttachment and a client.
    """
    #print("DEBUG: AttachmentForm.")  # Add a debug statement
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Client (Superadmin Only)"
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea
    )

    class Meta:
        model = Attachment
        fields = ['file', 'name']  # plus any other fields you want from Attachment

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # If editing an existing Attachment, attempt to load the TenantAttachment data
        if self.instance and self.instance.pk:
            try:
                tenant_attachment = self.instance.tenant_data
                self.fields['client'].initial = tenant_attachment.client.pk
                self.fields['description'].initial = tenant_attachment.description
            except TenantAttachment.DoesNotExist:
                pass

        # If user is not superadmin, hide the client field
        if self.request and self.request.user.client.pk != 1:
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = self.request.user.client.pk

    def save(self, commit=True):
        """
        1. Save the Attachment instance so it's committed to the DB.
        2. Create/update the TenantAttachment with the chosen client & description.
        """
        # Step 1: Save the Attachment to the database.
        attachment = super().save(commit=False)

        # We must do this so the 'attachment' has a primary key before referencing it in TenantAttachment
        attachment.save()

        # If commit=True, also save many-to-many data (like if the model had M2M fields).
        if commit:
            self.save_m2m()

        # Step 2: Determine the client. If none is chosen, fallback to the user's client or pk=1
        chosen_client = self.cleaned_data.get('client')
        if not chosen_client and self.request:
            chosen_client = self.request.user.client
        if not chosen_client:
            chosen_client = Client.objects.get(pk=1)

        # Create or update the TenantAttachment
        try:
            tenant_attachment = attachment.tenant_data
        except TenantAttachment.DoesNotExist:
            tenant_attachment = None

        if tenant_attachment is None:
            TenantAttachment.objects.create(
                attachment=attachment,
                client=chosen_client,
                description=self.cleaned_data.get('description', '')
            )
        else:
            tenant_attachment.client = chosen_client
            tenant_attachment.description = self.cleaned_data.get('description', '')
            tenant_attachment.save()

        return attachment


##Custom Admin class for Attachments
class CustomAttachmentAdmin(admin.ModelAdmin):
    """
    Custom admin for django-summernote's Attachment model.
    - Non-superadmin sees only attachments for their client,
      client field is hidden.
    - Superadmin can choose the client from a drop-down,
      can also set a description that is stored in TenantAttachment.
    """
    form = AttachmentForm
    list_display = ('name', 'get_client', 'get_description')

    def get_form(self, request, obj=None, **kwargs):
        # Pass `request` to the form so we can hide the client field for non-superadmin.
        kwargs['form'] = self.form
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs['request'] = request
                super().__init__(*args, **inner_kwargs)
        return FormWithRequest

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If user isn't superadmin, only show attachments for that user's client.
        if request.user.client.pk != 1:
            qs = qs.filter(tenant_data__client=request.user.client)
        return qs

    def get_client(self, obj):
        return obj.tenant_data.client.name if hasattr(obj, 'tenant_data') else 'No TenantAttachment'
    get_client.short_description = 'Client'

    def get_description(self, obj):
        return obj.tenant_data.description if hasattr(obj, 'tenant_data') else ''
    get_description.short_description = 'Description'

admin.site.register(Attachment, CustomAttachmentAdmin)