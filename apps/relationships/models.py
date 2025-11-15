from django.db import models
from django.conf import settings


class Relationship(models.Model):
    """
    Represents a person that the user has a relationship with.
    """
    RELATIONSHIP_TYPES = [
        ('FAMILY', 'Family'),
        ('FRIEND', 'Friend'),
        ('COLLEAGUE', 'Colleague'),
        ('ACQUAINTANCE', 'Acquaintance'),
        ('BUSINESS', 'Business Contact'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='relationships'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPES,
        default='OTHER'
    )
    notes_summary = models.TextField(blank=True, help_text='Summary of all notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.relationship_type})"

    class Meta:
        db_table = 'relationships'
        verbose_name = 'Relationship'
        verbose_name_plural = 'Relationships'
        ordering = ['-updated_at']
        unique_together = [['user', 'name', 'email']]
