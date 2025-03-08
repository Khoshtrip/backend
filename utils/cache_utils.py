from django.core.cache import cache
from django.utils.encoding import force_str
from django.conf import settings
import hashlib
import json

def generate_cache_key(view_name, request=None, *args, **kwargs):
    """
    Generate a unique cache key for a view based on its name and parameters.
    
    Args:
        view_name (str): The name of the view
        request (HttpRequest, optional): The request object to extract query parameters from
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        str: A unique cache key
    """
    key_parts = [view_name]
    
    if request is not None:
        key_parts.append(request.path)
        
        if request.GET:
            query_params = request.GET.copy()
            if 'page' in query_params:
                del query_params['page']
            if 'per_page' in query_params:
                del query_params['per_page']
            
            for key in sorted(query_params.keys()):
                key_parts.append(f"query:{key}:{query_params[key]}")
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            key_parts.append(f"user:{request.user.id}")
    
    # Add positional arguments
    for arg in args:
        key_parts.append(force_str(arg))
    
    # Add keyword arguments (sorted to ensure consistency)
    for k in sorted(kwargs.keys()):
        key_parts.append(f"{k}:{force_str(kwargs[k])}")
    
    # Join all parts and create a hash
    key_string = ':'.join(key_parts)
    return f"view_cache:{hashlib.md5(key_string.encode()).hexdigest()}"

def invalidate_cache_by_prefix(prefix):
    """
    Invalidate all cache keys that start with the given prefix.
    This works with Redis by scanning for keys with the given prefix.
    
    Args:
        prefix (str): The prefix to match against cache keys
    """
    # Get the Redis client
    if hasattr(cache, 'client') and hasattr(cache.client, 'get_client'):
        redis_client = cache.client.get_client()
        # Use Redis SCAN to find keys with the prefix
        cursor = '0'
        while cursor != 0:
            cursor, keys = redis_client.scan(cursor=cursor, match=f"{prefix}*", count=100)
            if keys:
                redis_client.delete(*keys)
            if cursor == '0' or cursor == 0:
                break

def cache_view_result(view_name, result, request=None, timeout=None, *args, **kwargs):
    """
    Manually cache a view result.
    
    Args:
        view_name (str): The name of the view
        result: The result to cache
        request (HttpRequest, optional): The request object to extract query parameters from
        timeout (int, optional): Cache timeout in seconds. Defaults to CACHE_MIDDLEWARE_SECONDS.
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
    """
    # Caching disabled
    # if timeout is None:
    #     timeout = getattr(settings, 'CACHE_MIDDLEWARE_SECONDS', 300)
    
    cache_key = generate_cache_key(view_name, request, *args, **kwargs)
    
    # if hasattr(result, 'accepted_renderer') and not getattr(result, '_is_rendered', False):
    #     result.render()
        
    # cache.set(cache_key, result, timeout)
    return cache_key

def set_cached_view_result(view_name, result, timeout=None, request=None, *args, **kwargs):
    """
    Manually set a cached view result.
    
    Args:
        view_name (str): The name of the view
        result: The result to cache
        timeout (int, optional): Cache timeout in seconds. Defaults to CACHE_MIDDLEWARE_SECONDS.
        request (HttpRequest, optional): The request object to extract query parameters from
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
    """
    # Caching disabled
    # if timeout is None:
    #     timeout = getattr(settings, 'CACHE_MIDDLEWARE_SECONDS', 300)
    
    cache_key = generate_cache_key(view_name, request, *args, **kwargs)
    
    # if hasattr(result, 'accepted_renderer') and not getattr(result, '_is_rendered', False):
    #     try:
    #         result.render()
    #     except Exception as e:
    #         # Log the error but don't fail
    #         print(f"Error rendering response: {str(e)}")
    #         return None
            
    # cache.set(cache_key, result, timeout)
    return cache_key

def get_cached_view_result(view_name, request=None, *args, **kwargs):
    """
    Retrieve a cached view result.
    
    Args:
        view_name (str): The name of the view
        request (HttpRequest, optional): The request object to extract query parameters from
        *args: Positional arguments to include in the key
        **kwargs: Keyword arguments to include in the key
        
    Returns:
        The cached result or None if not found
    """
    cache_key = generate_cache_key(view_name, request, *args, **kwargs)
    # Caching disabled
    # return cache.get(cache_key)
    return None

def get_cache_stats():
    """
    Get cache statistics from Redis.
    
    Returns:
        dict: Cache statistics
    """
    stats = {}
    
    # Get the Redis client
    if hasattr(cache, 'client') and hasattr(cache.client, 'get_client'):
        redis_client = cache.client.get_client()
        # Get Redis info
        info = redis_client.info()
        
        stats = {
            'used_memory': info.get('used_memory_human', 'N/A'),
            'used_memory_peak': info.get('used_memory_peak_human', 'N/A'),
            'total_connections_received': info.get('total_connections_received', 'N/A'),
            'total_commands_processed': info.get('total_commands_processed', 'N/A'),
            'keyspace_hits': info.get('keyspace_hits', 'N/A'),
            'keyspace_misses': info.get('keyspace_misses', 'N/A'),
        }
        
        # Calculate hit rate if possible
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        if hits or misses:
            hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0
            stats['hit_rate'] = f"{hit_rate:.2%}"
    
    return stats

def get_view_cache_key_pattern(view_name):
    """
    Get a pattern for matching all cache keys for a specific view.
    
    Args:
        view_name (str): The name of the view
        
    Returns:
        str: A pattern for matching cache keys
    """
    return f"view_cache:*{view_name}*"

def invalidate_model_caches(model_name, instance_id=None, related_models=None):
    """
    Invalidate all caches related to a specific model and its related models.
    
    Args:
        model_name (str): The name of the model (e.g., 'product', 'package')
        instance_id (int, optional): The ID of the specific instance
        related_models (list, optional): List of related model names to invalidate
    """
    if hasattr(cache, 'client') and hasattr(cache.client, 'get_client'):
        redis_client = cache.client.get_client()
        
        patterns = []
        
        patterns.append(f"view_cache:*{model_name}_list*")
        patterns.append(f"view_cache:*{model_name}s_list*")
        patterns.append(f"view_cache:*all_{model_name}s*")
        
        if instance_id:
            patterns.append(f"view_cache:*{model_name}_detail*")
            patterns.append(f"view_cache:*{model_name}*{instance_id}*")
        
        if related_models:
            for related_model in related_models:
                patterns.append(f"view_cache:*{related_model}_list*")
                patterns.append(f"view_cache:*{related_model}s_list*")
                patterns.append(f"view_cache:*all_{related_model}s*")
        
        if model_name == 'package':
            patterns.append(f"view_cache:*package_list*")
            patterns.append(f"view_cache:*package_detail*")
            patterns.append(f"view_cache:*user_purchase_history*")
        elif model_name == 'product':
            patterns.append(f"view_cache:*product_list*")
            patterns.append(f"view_cache:*product_detail*")
            patterns.append(f"view_cache:*all_products_list*")
            patterns.append(f"view_cache:*package_list*")
            patterns.append(f"view_cache:*package_detail*")
        elif model_name == 'image':
            # No need to invalidate image download cache as it's no longer cached
            pass
        
        print(f"Invalidating cache patterns: {patterns}")
        
        for pattern in patterns:
            cursor = '0'
            while cursor != 0:
                cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    print(f"Deleting keys: {keys}")
                    redis_client.delete(*keys)
                if cursor == '0' or cursor == 0:
                    break
        
        if model_name in ['product', 'package', 'transaction', 'purchasehistory']:
            print("Important model change detected, clearing entire cache")
            cache.clear() 