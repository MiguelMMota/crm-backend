from django.contrib import admin
from .models import Interaction


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'interaction_date', 'duration_minutes', 'created_at')
    list_filter = ('interaction_type', 'interaction_date', 'created_at')
    search_fields = ('user__username', 'summary', 'transcription')
    ordering = ('-interaction_date',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('relationships',)
