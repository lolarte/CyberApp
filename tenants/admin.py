from django import forms
from django.contrib import admin
from django.db.models import Subquery, OuterRef  # ✅ Import the missing Subquery & OuterRef
from django.contrib.auth.models import Group
#from .models import Client, TenantGroup, TenantAttachment, Attachment
from .models import Client, TenantGroup
from django.apps import apps
#Attachment = apps.get_model('mailtemplates', 'Attachment')

# 1. Unregister the default Group admin if it's already registered
try:
    admin.site.unregister(Group)
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
    """
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Client (Superadmin Only)"
    )
    description = forms.CharField(
        label="Description (Tenant-Specific)",
        required=False,
        #widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"})
        widget=forms.Textarea(attrs={"class": "ckeditor"})
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            try:
                tenant_group = self.instance.tenant_data
                self.fields['client'].initial = tenant_group.client.pk
                self.fields['description'].initial = tenant_group.description
            except TenantGroup.DoesNotExist:
                pass

        if self.request and self.request.user.client.pk != 1:
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = self.request.user.client.pk

    def save(self, commit=True):
        group = super().save(commit=commit)
        chosen_client = self.cleaned_data.get('client') or (
            self.request.user.client if self.request else None
        )
        if not chosen_client:
            chosen_client = Client.objects.get(pk=1)

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
    list_display = ('name', 'get_client', 'get_description')
    form = GroupForm

    def get_form(self, request, obj=None, **kwargs):
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
        return obj.tenant_data.client.name if hasattr(obj, 'tenant_data') else 'No TenantGroup'
    get_client.short_description = 'Client'

    def get_description(self, obj):
        return obj.tenant_data.description if hasattr(obj, 'tenant_data') else ''
    get_description.short_description = 'Description'


admin.site.register(Group, CustomGroupAdmin)

"""
class AttachmentForm(forms.ModelForm):
    ##A custom form for CKEditor 5's Attachment model.
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Client (Superadmin Only)"
    )
    description = forms.CharField(
        label="Description",
        required=False,
        #widget=CKEditor5Widget(attrs={"class": "django_ckeditor_5"})
        widget=forms.Textarea(attrs={"class": "ckeditor"})
    )

    class Meta:
        model = Attachment
        fields = ['file', 'name']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            try:
                tenant_attachment = self.instance.tenant_data
                self.fields['client'].initial = tenant_attachment.client.pk
                self.fields['description'].initial = tenant_attachment.description
            except TenantAttachment.DoesNotExist:
                pass

        if self.request and self.request.user.client.pk != 1:
            self.fields['client'].widget = forms.HiddenInput()
            self.fields['client'].initial = self.request.user.client.pk

    def save(self, commit=True):
        attachment = super().save(commit=False)
        attachment.save()

        if commit:
            self.save_m2m()

        chosen_client = self.cleaned_data.get('client')
        if not chosen_client and self.request:
            chosen_client = self.request.user.client
        if not chosen_client:
            chosen_client = Client.objects.get(pk=1)

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


class CustomAttachmentAdmin(admin.ModelAdmin):
    form = AttachmentForm
    list_display = ('name', 'get_client', 'get_description')

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = self.form
        form_class = super().get_form(request, obj, **kwargs)

        class FormWithRequest(form_class):
            def __init__(self2, *args, **inner_kwargs):
                inner_kwargs['request'] = request
                super().__init__(*args, **inner_kwargs)

        return FormWithRequest

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        #if request.user.client.pk != 1:
            #qs = qs.filter(tenant_data__client=request.user.client)
        #    qs = qs.filter(client=request.user.client)
        #return qs
        # ✅ Filter attachments that are linked to the logged-in user's client
        return qs.filter(
            id__in=Subquery(
                TenantAttachment.objects.filter(client=request.user.client).values("attachment_id")
            )
        )

    def get_client(self, obj):
        return obj.tenant_data.client.name if hasattr(obj, 'tenant_data') else 'No TenantAttachment'
    get_client.short_description = 'Client'

    def get_description(self, obj):
        return obj.tenant_data.description if hasattr(obj, 'tenant_data') else ''
    get_description.short_description = 'Description'


#admin.site.register(Attachment, CustomAttachmentAdmin)
"""