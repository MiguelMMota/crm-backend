from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Note CRUD operations"""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['relationship', 'status', 'importance_score', 'interaction']
    search_fields = ['note_text']
    ordering_fields = ['created_at', 'importance_score']
    ordering = ['-created_at']

    def get_queryset(self):
        # Only show notes for the current user
        return Note.objects.filter(user=self.request.user).select_related('relationship', 'interaction')
