from django.db import models

from core.choices import MatchStatus
from core.managers import MatchManager


class Match(models.Model):
    initiator = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='initiated_matches',
        verbose_name='Пользователь 1',
    )
    initiator_thread_id = models.PositiveBigIntegerField(
        'ID темы в чате с ботом',
        unique=True,
    )
    recipient = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='received_matches',
        verbose_name='Пользователь 2',
    )
    recipient_thread_id = models.PositiveBigIntegerField(
        'ID темы в чате с ботом',
        unique=True,
    )
    status = models.CharField(
        'Статус',
        choices=MatchStatus,
        max_length=20,
        default=MatchStatus.ACTIVE,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    objects = MatchManager()

    class Meta:
        verbose_name = 'Мэтч'
        verbose_name_plural = 'Мэтчи'

        unique_together = ('initiator', 'recipient')
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(initiator=models.F('recipient')),
                name='no_self_match',
            ),
        ]

    def __str__(self) -> str:
        return f'Mэтч ({self.pk})'
