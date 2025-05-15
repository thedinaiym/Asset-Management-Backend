import uuid
from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ('free', 'Free'),
    ('pending', 'Pending'),
    ('assigned', 'Assigned'),
]

class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='assets',
        on_delete=models.SET_NULL
    )
    pending_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='pending_assets',
        on_delete=models.SET_NULL
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='free')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"
