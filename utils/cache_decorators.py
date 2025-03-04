from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from .cache_utils import generate_cache_key, get_cached_view_result, cache_view_result

def cache_view(timeout=None, key_prefix=''):
    """
    Cache a view response based on the view name, request path, and query parameters.
    
    Args:
        timeout (int, optional): Cache timeout in seconds
        key_prefix (str, optional): Prefix for the cache key
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if request.method not in ('GET', 'HEAD') or (
                request.user.is_authenticated and 
                request.method != 'GET'
            ):
                return view_func(self, request, *args, **kwargs)
            
            # Generate a cache key
            view_name = f"{key_prefix}_{view_func.__name__}" if key_prefix else view_func.__name__
            cache_key = generate_cache_key(view_name, request, *args, **kwargs)
            
            cached_response = get_cached_view_result(view_name, request, *args, **kwargs)
            if cached_response is not None:
                return cached_response
            
            response = view_func(self, request, *args, **kwargs)
            
            if hasattr(response, 'status_code') and response.status_code == 404:
                return response
            
            cache_view_result(view_name, response, request, timeout, *args, **kwargs)
            
            return response
        
        return _wrapped_view
    
    return decorator

def cache_page_with_params(timeout=None):
    """
    A wrapper around cache_view that's similar to Django's cache_page but handles query parameters.
    
    Args:
        timeout (int, optional): Cache timeout in seconds
    """
    return cache_view(timeout=timeout)

class CacheMixin:
    """
    A mixin that adds caching to class-based views.
    
    Usage:
        class MyView(CacheMixin, APIView):
            cache_timeout = 300  # 5 minutes
            cache_key_prefix = 'my_view'
    """
    cache_timeout = None
    cache_key_prefix = ''
    
    def dispatch(self, request, *args, **kwargs):
        if request.method not in ('GET', 'HEAD') or (
            request.user.is_authenticated and 
            request.method != 'GET'
        ):
            return super().dispatch(request, *args, **kwargs)
        
        view_name = f"{self.cache_key_prefix}_{self.__class__.__name__}" if self.cache_key_prefix else self.__class__.__name__
        cache_key = generate_cache_key(view_name, request, *args, **kwargs)
        
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return cached_response
        
        response = super().dispatch(request, *args, **kwargs)
        
        if hasattr(response, 'status_code') and response.status_code == 404:
            return response
        
        if hasattr(response, 'data') and response.status_code == 200:
            cache.set(cache_key, response, self.cache_timeout)
        
        return response 