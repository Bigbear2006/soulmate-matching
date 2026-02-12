from django.contrib.auth.models import AbstractUser
from django.db import models

from core.managers import UserManager


class WebUser(AbstractUser):
    pass


class User(models.Model):
    id = models.PositiveBigIntegerField('Telegram ID', primary_key=True)
    first_name = models.CharField('Имя', max_length=255)
    last_name = models.CharField(
        'Фамилия',
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField('Ник', max_length=32, null=True, blank=True)
    is_premium = models.BooleanField('Есть премиум', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        username = self.first_name
        if self.username:
            username += f' (@{self.username})'
        return username
