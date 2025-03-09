from django.contrib import admin
from django import forms
#from django_ckeditor_5.widgets import CKEditor5Widget
from django.templatetags.static import static
from .models import EmailTemplate
from core.admin_mixins import TenantAdminMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Debugging CKEditor widget inside Django Admin
#print("\n===== DEBUG: Loading EmailTemplateAdmin in admin.py =====")

# Mixin to add custom CSS to Django Admin
class AdminCustomMixin:
    """Forces Django Admin to load Quill.js 2.0 with Image Resizing and Table Support"""
    class Media:
        js = (
            "https://cdn.jsdelivr.net/npm/quill@2.0.0/dist/quill.min.js",  # ✅ Load Quill 2.0
            "https://cdn.jsdelivr.net/gh/hunghg255/quill-resize-module/dist/quill-resize-image.min.js",  # ✅ Load Image Resize for Quill 2.0
             static("js/quill_init.js"),  # ✅ Load custom Quill initialization
        )
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/quill@2.0.0/dist/quill.snow.css",  # ✅ Load Quill 2.0 CSS
                static("css/admin_quill.css"),  # ✅ Load custom admin styles
            )
        }


class EmailTemplateForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        "class": "quill-editor",  # ✅ Ensures Quill is applied
    }))

    class Meta:
        model = EmailTemplate
        fields = '__all__'  # Include all model fields
        labels = {
            "name": _("Name"),  # ✅ Change label from "Name" to "From"
            "sender": _("Sender")  # ✅ Label for new Sender field
        }

    
    def __init__(self, *args, **kwargs):
#        print("\n===== DEBUG: Initializing EmailTemplateForm =====")
        super().__init__(*args, **kwargs)
#        print(f"DEBUG: CKEditor Upload URL → {self.fields['body'].widget.attrs.get('data-upload-url')}")

#class EmailTemplateAdmin(TenantAdminMixin, admin.ModelAdmin):
class EmailTemplateAdmin(AdminCustomMixin, admin.ModelAdmin):
    form = EmailTemplateForm 
    list_display = ('name', 'subject')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.client.pk != 1:
            qs = qs.filter(client=request.user.client)
            
        return qs

admin.site.register(EmailTemplate, EmailTemplateAdmin)
