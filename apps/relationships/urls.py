from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelationshipViewSet

router = DefaultRouter()
router.register(r'', RelationshipViewSet, basename='relationship')

urlpatterns = [
    path('', include(router.urls)),
]
