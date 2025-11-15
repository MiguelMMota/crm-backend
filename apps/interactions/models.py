from django.db import models
from django.conf import settings


class Interaction(models.Model):
    """
    Represents a call, meeting, or other interaction between the user and their relationships.
    """
    INTERACTION_TYPES = [
        ('VIDEO_CALL', 'Video Call'),
        ('PHONE_CALL', 'Phone Call'),
        ('LIVE_CHAT', 'Live Chat'),
        ('TEXT_MESSAGE', 'Text Message'),
        ('IN_PERSON', 'In Person'),
        ('USER_RECORD', 'User Record'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    relationships = models.ManyToManyField(
        'relationships.Relationship',
        related_name='interactions',
        help_text='People involved in this interaction'
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        default='OTHER'
    )
    interaction_date = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text='Duration in minutes (if applicable)'
    )
    transcription = models.TextField(
        blank=True,
        help_text='Full transcription of the interaction'
    )
    summary = models.TextField(
        blank=True,
        help_text='AI-generated summary of the interaction'
    )
    video_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Path to stored video file'
    )
    audio_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Path to stored audio file'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.interaction_type} on {self.interaction_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        db_table = 'interactions'
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        ordering = ['-interaction_date']
