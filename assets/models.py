from django.db import models
from django.contrib.auth.models import User
import uuid

STATUS_CHOICES = [
    ('pending',  'На рассмотрении'),
    ('assigned', 'Назначено'),
    ('free',     'Свободно'),
]

class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_type = models.CharField(max_length=50, help_text="Тип имущества (мебель, устройство и т.д.)")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='assets/photos/', blank=True, null=True)

    owner = models.ForeignKey(
        User,
        related_name='assets',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pending_user = models.ForeignKey(
        User,
        related_name='pending_assets',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Кто запросил сейчас"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',     # теперь будет всегда хотя бы 'pending'
        null=True,             # и, на всякий случай, разрешаем NULL
        blank=True
    )
    def __str__(self):
        return self.title
