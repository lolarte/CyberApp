from django.urls import path
from .views import quill_image_upload

urlpatterns = [
    path("quill/upload/", quill_image_upload, name="quill_image_upload"),
]
