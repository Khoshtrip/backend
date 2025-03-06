from django.utils.cache import patch_response_headers
from django.conf import settings

class CacheControlMiddleware:
    """
    Middleware to add Cache-Control headers to responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        if request.path.startswith('/admin/'):
            patch_response_headers(response, cache_timeout=0)
            return response
            
        if request.user.is_authenticated:
            patch_response_headers(response, cache_timeout=0)
            return response
            
        if request.method in ('GET', 'HEAD') and response.status_code == 200:
            cache_timeout = getattr(settings, 'CACHE_MIDDLEWARE_SECONDS', 300)
            patch_response_headers(response, cache_timeout=cache_timeout)
            
        return response 