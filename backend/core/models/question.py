from django.db import models

from core.choices import QuestionKey
from core.managers import QuestionManager


class Question(models.Model):
    key = models.CharField(
        'Ключ',
        choices=QuestionKey,
        max_length=50,
        unique=True,
    )
    text = models.TextField('Текст')
    bot_response = models.TextField('Ответ бота', blank=True)
    order = models.PositiveIntegerField('Номер', default=1)
    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(
        'core.Question',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    text = models.CharField('Ответ', max_length=255)
    bot_response = models.TextField('Ответ бота', blank=True)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'

    def __str__(self) -> str:
        return self.text[:50]


class ProfileAnswer(models.Model):
    profile = models.ForeignKey(
        'core.Profile',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Профиль',
    )
    answer = models.ForeignKey(
        'core.Answer',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Ответ',
    )

    class Meta:
        unique_together = ('profile', 'answer')
        verbose_name = 'Ответ на вопрос анкеты'
        verbose_name_plural = 'Ответы на вопрос анкеты'

    def __str__(self) -> str:
        return f'Ответ на вопрос анкеты ({self.pk})'
