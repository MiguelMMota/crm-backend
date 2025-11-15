from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('relationship', 'user', 'status', 'importance_score', 'note_text_preview', 'created_at')
    list_filter = ('status', 'importance_score', 'created_at')
    search_fields = ('note_text', 'relationship__name', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def note_text_preview(self, obj):
        return obj.note_text[:100] + '...' if len(obj.note_text) > 100 else obj.note_text
    note_text_preview.short_description = 'Note Preview'
