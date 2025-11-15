"""
URL configuration for CRM backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/relationships/', include('apps.relationships.urls')),
    path('api/interactions/', include('apps.interactions.urls')),
    path('api/notes/', include('apps.notes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
