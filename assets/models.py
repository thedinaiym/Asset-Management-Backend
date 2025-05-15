
from django.db import models
from django.contrib.auth.models import User
import uuid
class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_type = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='assets/', blank=True, null=True)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='assets', null=True, blank=True
    )
    pending_user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='pending_assets', null=True, blank=True
    )

    STATUS_CHOICES = [
        ('free', 'Свободно'),
        ('pending', 'Ожидание'),
        ('assigned', 'Назначено'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)

    # Для возврата/бере́на
    action_type = models.CharField(max_length=10, choices=[('take','Беру'),('return','Возвращаю')], blank=True)
    linked_asset = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='returns', help_text='При возврате — ссылка на взятую ранее'
    )

    # Оценка состояния при возврате
    rating_before = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_after = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title