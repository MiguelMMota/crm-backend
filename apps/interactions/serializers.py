from rest_framework import serializers
from .models import Interaction
from apps.relationships.models import Relationship
from apps.relationships.serializers import RelationshipSerializer


class InteractionSerializer(serializers.ModelSerializer):
    """Serializer for Interaction model"""
    relationships_data = RelationshipSerializer(source='relationships', many=True, read_only=True)
    relationship_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Relationship.objects.none(),  # Default empty, set dynamically in __init__
        source='relationships',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for relationship_ids to current user's relationships
        if 'request' in self.context:
            self.fields['relationship_ids'].queryset = Relationship.objects.filter(
                user=self.context['request'].user
            )

    class Meta:
        model = Interaction
        fields = (
            'id', 'user', 'relationships_data', 'relationship_ids',
            'interaction_type', 'interaction_date', 'duration_minutes',
            'transcription', 'summary', 'video_path', 'audio_path',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'interaction_date', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        relationships = validated_data.pop('relationships', [])
        interaction = Interaction.objects.create(**validated_data)
        interaction.relationships.set(relationships)
        return interaction


class InteractionDetailSerializer(InteractionSerializer):
    """Detailed serializer with full transcription"""
    notes_count = serializers.SerializerMethodField()

    class Meta(InteractionSerializer.Meta):
        fields = InteractionSerializer.Meta.fields + ('notes_count',)

    def get_notes_count(self, obj):
        return obj.notes.filter(status='ACTIVE').count()
