from django.http import JsonResponse
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
from django_summernote.forms import UploadForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import TenantAttachment, Client, Attachment


@csrf_exempt
def custom_attachment_upload(request):
    """
    A custom upload endpoint for django-summernote that also creates
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
            return JsonResponse({'status': 'error', 'msg': 'No file uploaded'}, status=400)

        # Get the first file key dynamically
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
        if request.user.is_authenticated:
            if hasattr(request.user, 'client') and request.user.client.pk != 1:
                client = request.user.client
            else:
                # Superadmin or fallback
                client = Client.objects.get(pk=1)
        else:
            # If user isn't logged in, fallback to client=1
            client = Client.objects.get(pk=1)

        print(f"DEBUG: Attachment saved at {attachment.file.url}")
        print(f"DEBUG: Client assigned: {client}")

        # Create or update TenantAttachment
        TenantAttachment.objects.create(
            attachment=attachment,
            client=client
        )

        print("DEBUG: TenantAttachment created successfully.")
        print(f"DEBUG: Returning URL: {attachment.file.url}")

        # Build the JSON response the Summernote editor expects
        current_site = Site.objects.get_current()
        absolute_url = f"https://{current_site.domain}{attachment.file.url}"
        # Construct the relative file URL
        file_url = request.build_absolute_uri(attachment.file.url)

        # Remove the domain part to keep it relative
        file_url = file_url.replace(request.build_absolute_uri('/'), '/')

        #print("Absolute URL: ",absolute_url)
        print("Relative URL: ",file_url)
        
        response_data = {
            'status': 'success',
            'url': attachment.file.url,  # Ensure it's a correct relative path
            'name': attachment.name if attachment.name else attachment.file.name
        }

        print(f"DEBUG: JSON Response Data: {response_data}")  # See the actual data

        return JsonResponse(response_data)

    print("ERROR: Invalid request (method not POST or missing files).")
    return JsonResponse({'status': 'error', 'msg': 'Invalid request'}, status=400)


