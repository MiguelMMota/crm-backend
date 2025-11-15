from rest_framework import serializers
from .models import Relationship


class RelationshipSerializer(serializers.ModelSerializer):
    """Serializer for Relationship model"""

    class Meta:
        model = Relationship
        fields = (
            'id', 'user', 'name', 'email', 'phone_number',
            'relationship_type', 'notes_summary', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RelationshipDetailSerializer(RelationshipSerializer):
    """Detailed serializer with nested notes"""
    notes_count = serializers.SerializerMethodField()
    recent_interactions_count = serializers.SerializerMethodField()

    class Meta(RelationshipSerializer.Meta):
        fields = RelationshipSerializer.Meta.fields + ('notes_count', 'recent_interactions_count')

    def get_notes_count(self, obj):
        return obj.notes.filter(status='ACTIVE').count()

    def get_recent_interactions_count(self, obj):
        return obj.interactions.count()
