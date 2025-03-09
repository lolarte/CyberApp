import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

@csrf_exempt
def quill_image_upload(request):
    """Handles image uploads from Quill.js and saves them in /media/uploads/"""
    if request.method == "POST" and request.FILES:
        uploaded_file = request.FILES["image"]
        
        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        upload_path = os.path.join("uploads", filename)

        # Save the image in the media/uploads/ directory
        file_path = default_storage.save(upload_path, ContentFile(uploaded_file.read()))

        # Return the image URL to Quill
        return JsonResponse({
            "success": True,
            "url": f"{settings.MEDIA_URL}{file_path}"
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
