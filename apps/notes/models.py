from django.db import models
from django.conf import settings


class Note(models.Model):
    """
    Auto-generated notes from interactions about specific relationships.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ARCHIVED', 'Archived'),
        ('DELETED', 'Deleted'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    relationship = models.ForeignKey(
        'relationships.Relationship',
        on_delete=models.CASCADE,
        related_name='notes'
    )
    interaction = models.ForeignKey(
        'interactions.Interaction',
        on_delete=models.CASCADE,
        related_name='notes',
        null=True,
        blank=True
    )
    note_text = models.TextField(help_text='The actual note content')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    importance_score = models.IntegerField(
        default=5,
        help_text='Importance score (1-10), used for sorting/filtering'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.relationship.name}: {self.note_text[:50]}"

    class Meta:
        db_table = 'notes'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['relationship', 'status']),
            models.Index(fields=['user', 'status']),
        ]
