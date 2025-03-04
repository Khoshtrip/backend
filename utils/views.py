from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from .cache_utils import get_cache_stats
from .cache_monitoring import get_detailed_cache_stats, cache_metrics
import json
import os
from django.conf import settings

class CacheStatsView(APIView):
    """
    View to get Redis cache statistics.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Get Redis cache statistics.
        """
        return Response(get_detailed_cache_stats())
        
class ClearCacheView(APIView):
    """
    View to clear the entire cache.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Clear the entire cache.
        """
        cache.clear()
        
        return Response({
            'status': 'success',
            'message': 'Cache cleared successfully'
        }, status=status.HTTP_200_OK)

class CacheLogsView(APIView):
    """
    View to get cache logs.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Get cache logs.
        """
        log_file_path = os.path.join(settings.BASE_LOG_DIR, 'cache_monitoring.log')
        
        if not os.path.exists(log_file_path):
            return Response({"message": "No cache logs found"}, status=status.HTTP_404_NOT_FOUND)
        
        lines = int(request.query_params.get('lines', 100))
        
        logs = []
        try:
            with open(log_file_path, 'r') as f:
                for line in f.readlines()[-lines:]:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        logs.append({"raw": line.strip()})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"logs": logs, "count": len(logs)})

class CacheMetricsResetView(APIView):
    """
    View to reset cache metrics.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Reset cache metrics.
        """
        cache_metrics.reset()
        
        return Response({
            'status': 'success',
            'message': 'Cache metrics reset successfully'
        }, status=status.HTTP_200_OK)

class CacheAnalyticsView(APIView):
    """
    View to get cache analytics.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Get cache analytics.
        """
        metrics = cache_metrics.get_metrics_summary()
        
        hit_rate = cache_metrics.get_hit_rate()
        hits = cache_metrics._get_counter('hits')
        avg_response_time = cache_metrics.get_average_response_time()
        
        estimated_time_saved = hits * avg_response_time * 0.9 if hits > 0 else 0
        
        views = cache_metrics.get_all_views()
        view_hit_rates = [
            {
                'view': view,
                'hit_rate': cache_metrics.get_view_hit_rate(view),
                'hits': cache_metrics._get_counter(f"view:{view}:hits"),
                'misses': cache_metrics._get_counter(f"view:{view}:misses")
            }
            for view in views
        ]
        
        top_views_by_hit_rate = sorted(
            [v for v in view_hit_rates if v['hits'] + v['misses'] > 10],  # Only include views with significant traffic
            key=lambda x: x['hit_rate'],
            reverse=True
        )[:5]  # Top 5

        view_response_times = [
            {
                'view': view,
                'avg_response_time': cache_metrics.get_view_average_response_time(view),
                'hits': cache_metrics._get_counter(f"view:{view}:hits")
            }
            for view in views
        ]
        
        top_views_by_response_time = sorted(
            [v for v in view_response_times if v['hits'] > 10],  # Only include views with significant cache hits
            key=lambda x: (x['avg_response_time'], -x['hits'])
        )[:5]  # Top 5
        
        analytics = {
            'summary': {
                'total_requests': metrics['total_requests'],
                'hit_rate': metrics['hit_rate'],
                'average_response_time': metrics['average_response_time'],
                'estimated_time_saved': f"{estimated_time_saved:.2f} seconds"
            },
            'top_views_by_hit_rate': top_views_by_hit_rate,
            'top_views_by_response_time': top_views_by_response_time,
            'all_metrics': metrics
        }
        
        return Response(analytics) 