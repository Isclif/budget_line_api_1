from django.http import HttpResponseForbidden

# ALLOWED_IPS = ['172.19.120.186']
ALLOWED_IPS = ['127.0.0.1', '172.19.120.186']

class RestrictIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        if ip not in ALLOWED_IPS:
            return HttpResponseForbidden("Forbidden: Your IP is not allowed.")
        response = self.get_response(request)
        return response