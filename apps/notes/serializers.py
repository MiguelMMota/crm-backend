from rest_framework import serializers
from .models import Note
from apps.relationships.models import Relationship
from apps.relationships.serializers import RelationshipSerializer


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model"""
    relationship_data = RelationshipSerializer(source='relationship', read_only=True)
    relationship_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Relationship.objects.none(),  # Default empty, set dynamically in __init__
        source='relationship',
        required=False
    )

    class Meta:
        model = Note
        fields = (
            'id', 'user', 'relationship_data', 'relationship_id',
            'interaction', 'note_text', 'status', 'importance_score',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            self.fields['relationship_id'].queryset = Relationship.objects.filter(
                user=self.context['request'].user
            )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
