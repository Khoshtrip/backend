import time
import logging
import json
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from .cache_utils import get_cache_stats, generate_cache_key, cache_view_result

logger = logging.getLogger('cache_monitoring')

class RedisCacheMetrics:
    """Class to track and store cache metrics in Redis"""
    
    def __init__(self):
        self.redis_prefix = 'cache_metrics:'
    
    def _get_redis_client(self):
        """Get the Redis client from the cache backend"""
        if hasattr(cache, 'client') and hasattr(cache.client, 'get_client'):
            return cache.client.get_client()
        return None
    
    def _increment_counter(self, key, increment=1):
        """Increment a counter in Redis"""
        redis_client = self._get_redis_client()
        if redis_client:
            if not isinstance(increment, int):
                try:
                    if key.endswith('_response_time'):
                        increment = int(increment * 1000)
                    else:
                        increment = int(increment)
                except (ValueError, TypeError):
                    increment = 1
            return redis_client.incr(f"{self.redis_prefix}{key}", increment)
        return 0
    
    def _add_to_sorted_set(self, set_name, member, score):
        """Add a member to a sorted set in Redis"""
        redis_client = self._get_redis_client()
        if redis_client:
            try:
                score = float(score)
            except (ValueError, TypeError):
                score = 0.0
                
            if not isinstance(member, str):
                member = str(member)
                
            return redis_client.zadd(f"{self.redis_prefix}{set_name}", {member: score})
        return 0
    
    def _get_counter(self, key):
        """Get a counter value from Redis"""
        redis_client = self._get_redis_client()
        if redis_client:
            value = redis_client.get(f"{self.redis_prefix}{key}")
            return int(value) if value else 0
        return 0
    
    def _get_sorted_set_members(self, set_name):
        """Get all members of a sorted set from Redis"""
        redis_client = self._get_redis_client()
        if redis_client:
            return redis_client.zrange(f"{self.redis_prefix}{set_name}", 0, -1, withscores=True)
        return []
    
    def record_hit(self, view_name, response_time):
        """Record a cache hit"""
        self._increment_counter('hits')
        self._increment_counter('requests')
        self._increment_counter(f"view:{view_name}:hits")
        self._increment_counter(f"view:{view_name}:requests")
        
        self._add_to_sorted_set('response_times', time.time(), response_time)
        self._add_to_sorted_set(f"view:{view_name}:response_times", time.time(), response_time)
        
        self._increment_counter('total_response_time', response_time)
        self._increment_counter(f"view:{view_name}:total_response_time", response_time)
    
    def record_miss(self, view_name, response_time):
        """Record a cache miss"""
        self._increment_counter('misses')
        self._increment_counter('requests')
        self._increment_counter(f"view:{view_name}:misses")
        self._increment_counter(f"view:{view_name}:requests")
        
        self._add_to_sorted_set('response_times', time.time(), response_time)
        self._add_to_sorted_set(f"view:{view_name}:response_times", time.time(), response_time)
        
        self._increment_counter('total_response_time', response_time)
        self._increment_counter(f"view:{view_name}:total_response_time", response_time)
    
    def get_hit_rate(self):
        """Get the cache hit rate"""
        hits = self._get_counter('hits')
        requests = self._get_counter('requests')
        
        if requests == 0:
            return 0
        return hits / requests
    
    def get_average_response_time(self):
        """Get the average response time"""
        total_time = self._get_counter('total_response_time')
        requests = self._get_counter('requests')
        
        if requests == 0:
            return 0
        return total_time / requests
    
    def get_view_hit_rate(self, view_name):
        """Get the hit rate for a specific view"""
        hits = self._get_counter(f"view:{view_name}:hits")
        requests = self._get_counter(f"view:{view_name}:requests")
        
        if requests == 0:
            return 0
        return hits / requests
    
    def get_view_average_response_time(self, view_name):
        """Get the average response time for a specific view"""
        total_time = self._get_counter(f"view:{view_name}:total_response_time")
        requests = self._get_counter(f"view:{view_name}:requests")
        
        if requests == 0:
            return 0
        return total_time / requests
    
    def get_all_views(self):
        """Get a list of all views that have metrics"""
        redis_client = self._get_redis_client()
        if redis_client:
            keys = redis_client.keys(f"{self.redis_prefix}view:*:hits")
            return [key.decode().split(':')[2] for key in keys]
        return []
    
    def get_metrics_summary(self):
        """Get a summary of all metrics"""
        views = self.get_all_views()
        
        return {
            'total_requests': self._get_counter('requests'),
            'hits': self._get_counter('hits'),
            'misses': self._get_counter('misses'),
            'hit_rate': f"{self.get_hit_rate():.2%}",
            'average_response_time': f"{self.get_average_response_time():.6f} seconds",
            'view_metrics': {
                view_name: {
                    'hits': self._get_counter(f"view:{view_name}:hits"),
                    'misses': self._get_counter(f"view:{view_name}:misses"),
                    'hit_rate': f"{self.get_view_hit_rate(view_name):.2%}",
                    'average_response_time': f"{self.get_view_average_response_time(view_name):.6f} seconds"
                }
                for view_name in views
            }
        }
    
    def reset(self):
        """Reset all metrics"""
        redis_client = self._get_redis_client()
        if redis_client:
            keys = redis_client.keys(f"{self.redis_prefix}*")
            if keys:
                redis_client.delete(*keys)

cache_metrics = RedisCacheMetrics()

def log_cache_access(view_name, cache_hit, response_time, cache_key=None, user_id=None, query_params=None):
    """
    Log cache access with detailed information
    
    Args:
        view_name (str): Name of the view
        cache_hit (bool): Whether the request was a cache hit
        response_time (float): Time taken to serve the request
        cache_key (str, optional): The cache key used
        user_id (int, optional): ID of the user making the request
        query_params (dict, optional): Query parameters in the request
    """
    try:
        log_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'view': view_name,
            'cache_hit': cache_hit,
            'response_time': f"{response_time:.6f}s",
            'cache_key': cache_key,
            'user_id': user_id,
            'query_params': query_params
        }
        
        logger.info(json.dumps(log_data))
        
        try:
            if cache_hit:
                cache_metrics.record_hit(view_name, response_time)
            else:
                cache_metrics.record_miss(view_name, response_time)
        except Exception as e:
            logger.error(f"Error updating cache metrics: {str(e)}")
    except Exception as e:
        logger.error(f"Error in log_cache_access: {str(e)}")

def monitored_cache_view(timeout=None, key_prefix=''):
    """
    A decorator that caches a view and monitors cache performance
    
    Args:
        timeout (int, optional): Cache timeout in seconds
        key_prefix (str, optional): Prefix for the cache key
    """
    from .cache_decorators import cache_view
    
    def decorator(view_func):
        cached_func = cache_view(timeout=timeout, key_prefix=key_prefix)(view_func)
        
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            start_time = time.time()
            
            view_name = f"{key_prefix}_{view_func.__name__}" if key_prefix else view_func.__name__
            cache_key = generate_cache_key(view_name, request, *args, **kwargs)
            
            cached_response = cache.get(cache_key)
            cache_hit = cached_response is not None
            
            response = cached_func(self, request, *args, **kwargs)
            
            response_time = time.time() - start_time
            
            query_params = dict(request.GET.items()) if request.GET else None
            
            user_id = request.user.id if request.user and request.user.is_authenticated else None
            
            if hasattr(response, 'status_code') and response.status_code == 404:
                cache.delete(cache_key)
                print(f"Not caching 404 response for {view_name}")
            
            log_cache_access(
                view_name=view_name,
                cache_hit=cache_hit,
                response_time=response_time,
                cache_key=cache_key,
                user_id=user_id,
                query_params=query_params
            )
            
            return response
        
        return _wrapped_view
    
    return decorator

def get_detailed_cache_stats():
    """
    Get detailed cache statistics including Redis stats and application metrics
    
    Returns:
        dict: Detailed cache statistics
    """
    redis_stats = get_cache_stats()
    
    app_metrics = cache_metrics.get_metrics_summary()
    
    return {
        'redis_stats': redis_stats,
        'app_metrics': app_metrics,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

class MonitoredCacheMixin:
    """
    A mixin that adds caching with monitoring to class-based views.
    
    Usage:
        class MyView(MonitoredCacheMixin, APIView):
            cache_timeout = 300  # 5 minutes
            cache_key_prefix = 'my_view'
    """
    cache_timeout = None
    cache_key_prefix = ''
    
    def dispatch(self, request, *args, **kwargs):
        # Don't cache for authenticated users unless they're just reading
        if request.method not in ('GET', 'HEAD') or (
            request.user.is_authenticated and 
            request.method != 'GET'
        ):
            return super().dispatch(request, *args, **kwargs)
        
        start_time = time.time()
        
        view_name = f"{self.cache_key_prefix}_{self.__class__.__name__}" if self.cache_key_prefix else self.__class__.__name__
        cache_key = generate_cache_key(view_name, request, *args, **kwargs)
        
        cached_response = cache.get(cache_key)
        cache_hit = cached_response is not None
        
        if cache_hit:
            response = cached_response
        else:
            response = super().dispatch(request, *args, **kwargs)
            
            if hasattr(response, 'status_code') and response.status_code == 404:
                cache.delete(cache_key)
                print(f"Not caching 404 response for {view_name}")
            else:
                if hasattr(response, 'data') and response.status_code == 200:
                    try:
                        if hasattr(response, 'accepted_renderer') and not getattr(response, '_is_rendered', False):
                            response.render()
                        cache.set(cache_key, response, self.cache_timeout)
                    except Exception as e:
                        logger.error(f"Error caching response: {str(e)}")
        
        response_time = time.time() - start_time
        
        query_params = dict(request.GET.items()) if request.GET else None
        
        user_id = request.user.id if request.user and request.user.is_authenticated else None
        
        try:
            log_cache_access(
                view_name=view_name,
                cache_hit=cache_hit,
                response_time=response_time,
                cache_key=cache_key,
                user_id=user_id,
                query_params=query_params
            )
        except Exception as e:
            logger.error(f"Error logging cache access: {str(e)}")
        
        return response 