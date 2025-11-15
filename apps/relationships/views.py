from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Relationship
from .serializers import RelationshipSerializer, RelationshipDetailSerializer


class RelationshipViewSet(viewsets.ModelViewSet):
    """ViewSet for Relationship CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['relationship_type']
    search_fields = ['name', 'email', 'phone_number']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        # Only show relationships for the current user
        return Relationship.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RelationshipDetailSerializer
        return RelationshipSerializer
