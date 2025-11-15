from django.contrib import admin
from .models import Relationship


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'relationship_type', 'email', 'phone_number', 'created_at')
    list_filter = ('relationship_type', 'created_at')
    search_fields = ('name', 'email', 'phone_number', 'user__username')
    ordering = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at')
