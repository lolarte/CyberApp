from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .models import TenantAttachment, Client, Attachment

@csrf_exempt
def custom_attachment_upload(request):
    """
    A custom upload endpoint for CKEditor 5 that also creates
    a TenantAttachment for the user's client.
    """

    print("DEBUG: ===== Entered custom_attachment_upload route =====")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request content-type: {request.content_type}")

    if request.method == 'POST':
        print(f"DEBUG: Request POST data: {dict(request.POST)}")
        print(f"DEBUG: Request FILES data: {request.FILES.keys()}")

        if not request.FILES:
            print("ERROR: No files detected in request.")
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # Get the uploaded file dynamically
        file_key = list(request.FILES.keys())[0]
        uploaded_file = request.FILES[file_key]

        print(f"DEBUG: Detected uploaded file key: {file_key}")
        print(f"DEBUG: Uploaded file name: {uploaded_file.name}")

        # Manually save the uploaded file
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", ContentFile(uploaded_file.read()))

        # Create an Attachment object manually
        attachment = Attachment.objects.create(
            file=file_path,
            name=uploaded_file.name
        )

        # Determine the user’s client
        if request.user.is_authenticated and hasattr(request.user, 'client') and request.user.client.pk != 1:
            client = request.user.client
        else:
            client = Client.objects.get(pk=1)  # Fallback client

        print(f"DEBUG: Attachment saved at {attachment.file.url}")
        print(f"DEBUG: Client assigned: {client}")

        # Create or update TenantAttachment
        TenantAttachment.objects.create(
            attachment=attachment,
            client=client
        )

        print("DEBUG: TenantAttachment created successfully.")
        
        # Build JSON response CKEditor 5 expects
        response_data = {
            'url': attachment.file.url,  # CKEditor 5 expects 'url' in the response
        }

        print(f"DEBUG: JSON Response Data: {response_data}")  # Debugging info

        return JsonResponse(response_data)

    print("ERROR: Invalid request (method not POST or missing files).")
    return JsonResponse({'error': 'Invalid request'}, status=400)
