from django.db import models


class Question(models.Model):
    key = models.CharField('Ключ', max_length=50, unique=True)
    text = models.TextField('Текст')
    bot_response = models.TextField('Ответ бота', blank=True)
    order = models.PositiveIntegerField('Номер', default=1)

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


class UserAnswer(models.Model):
    profile = models.ForeignKey(
        'core.Profile',
        on_delete=models.CASCADE,
        related_name='answers',
    )
    answer = models.ForeignKey(
        'core.Answer',
        on_delete=models.CASCADE,
        related_name='users',
    )

    class Meta:
        unique_together = ('profile', 'answer')
