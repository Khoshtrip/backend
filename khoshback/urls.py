from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_prometheus import exports

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authorization.urls')),
    path('api/', include('product.urls')),
    path('api/', include('package.urls')),
    path('api/', include('utils.urls')),
    path('metrics/', exports.ExportToDjangoView, name='prometheus-django-metrics'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)