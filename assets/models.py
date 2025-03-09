from django.db import models
from django.contrib.auth.models import User
import uuid

class Asset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_type = models.CharField(max_length=50, help_text="Тип имущества (мебель, устройство и т.д.)")
    title = models.CharField(max_length=100, help_text="Название объекта")
    description = models.TextField(blank=True, help_text="Описание объекта")
    photo = models.ImageField(upload_to='assets/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets', help_text="Владелец объекта")

    def __str__(self):
        return self.title
