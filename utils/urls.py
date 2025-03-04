from django.urls import path
from .views import (
    CacheStatsView, 
    ClearCacheView, 
    CacheLogsView, 
    CacheMetricsResetView, 
    CacheAnalyticsView
)

urlpatterns = [
    path('cache/stats/', CacheStatsView.as_view(), name='cache-stats'),
    path('cache/clear/', ClearCacheView.as_view(), name='cache-clear'),
    path('cache/logs/', CacheLogsView.as_view(), name='cache-logs'),
    path('cache/metrics/reset/', CacheMetricsResetView.as_view(), name='cache-metrics-reset'),
    path('cache/analytics/', CacheAnalyticsView.as_view(), name='cache-analytics'),
] 