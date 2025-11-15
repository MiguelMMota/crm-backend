from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Interaction
from .serializers import InteractionSerializer, InteractionDetailSerializer


class InteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for Interaction CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['interaction_type', 'interaction_date']
    search_fields = ['summary', 'transcription']
    ordering_fields = ['interaction_date', 'created_at']
    ordering = ['-interaction_date']

    def get_queryset(self):
        # Only show interactions for the current user
        return Interaction.objects.filter(user=self.request.user).prefetch_related('relationships')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InteractionDetailSerializer
        return InteractionSerializer
