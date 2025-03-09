import threading
from tenants.models import Client

_thread_locals = threading.local()

def get_current_client():
    return getattr(_thread_locals, 'client', None)

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Example: use subdomain as the client's slug.
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]  # Assuming URL like client.example.com
        try:
            client = Client.objects.get(slug=subdomain)
        except Client.DoesNotExist:
            #client = None
            #client = Client.objects.first()  
            if request.path.startswith('/admin/'):
                client = Client.objects.get(pk=1)
            else:
                client = Client.objects.first()
        _thread_locals.client = client
        request.client = client  # Optionally attach to the request
        response = self.get_response(request)
        #print("TenantMiddleware set client:", client)  # Debug print
        return response
