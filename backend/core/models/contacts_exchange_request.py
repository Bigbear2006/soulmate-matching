from django.db import models

from core.choices import ExchangeStatus
from core.managers.contacts_exchange_request import (
    ContactsExchangeRequestManager,
)


class ContactsExchangeRequest(models.Model):
    match = models.ForeignKey(
        'core.Match',
        on_delete=models.CASCADE,
        related_name='contacts_exchange_requests',
    )
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='contacts_exchange_requests',
    )
    status = models.CharField(
        'Статус',
        choices=ExchangeStatus,
        max_length=20,
        default=ExchangeStatus.PENDING,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = ContactsExchangeRequestManager()

    class Meta:
        verbose_name = 'Обмен контактами'
        verbose_name_plural = 'Обмены контактами'

    def __str__(self) -> str:
        return f'Обмен контактами ({self.pk}'
