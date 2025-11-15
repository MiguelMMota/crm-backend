from django.contrib import admin
from .models import FaceSignature, VoiceSignature


@admin.register(FaceSignature)
class FaceSignatureAdmin(admin.ModelAdmin):
    list_display = ('relationship', 'confidence_score', 'image_path', 'created_at')
    list_filter = ('created_at', 'confidence_score')
    search_fields = ('relationship__name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VoiceSignature)
class VoiceSignatureAdmin(admin.ModelAdmin):
    list_display = ('relationship', 'confidence_score', 'audio_path', 'created_at')
    list_filter = ('created_at', 'confidence_score')
    search_fields = ('relationship__name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
