from django.db import models
from pgvector.django import VectorField


class FaceSignature(models.Model):
    """
    Stores face embeddings for relationship identification.
    Uses pgvector for similarity search.
    """
    relationship = models.ForeignKey(
        'relationships.Relationship',
        on_delete=models.CASCADE,
        related_name='face_signatures'
    )
    embedding = VectorField(
        dimensions=128,
        help_text='Face embedding vector (128 dimensions for face_recognition library)'
    )
    image_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Path to the source image'
    )
    confidence_score = models.FloatField(
        default=1.0,
        help_text='Confidence score of the face detection (0-1)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Face signature for {self.relationship.name}"

    class Meta:
        db_table = 'face_signatures'
        verbose_name = 'Face Signature'
        verbose_name_plural = 'Face Signatures'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['relationship']),
        ]


class VoiceSignature(models.Model):
    """
    Stores voice embeddings for speaker identification.
    Uses pgvector for similarity search.
    """
    relationship = models.ForeignKey(
        'relationships.Relationship',
        on_delete=models.CASCADE,
        related_name='voice_signatures'
    )
    embedding = VectorField(
        dimensions=512,
        help_text='Voice embedding vector (dimensions depend on the model used)'
    )
    audio_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Path to the source audio sample'
    )
    confidence_score = models.FloatField(
        default=1.0,
        help_text='Confidence score of the voice detection (0-1)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Voice signature for {self.relationship.name}"

    class Meta:
        db_table = 'voice_signatures'
        verbose_name = 'Voice Signature'
        verbose_name_plural = 'Voice Signatures'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['relationship']),
        ]
