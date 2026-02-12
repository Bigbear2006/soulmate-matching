from django.db import models

from core.choices import (
    CareerFocus,
    Gender,
    Lifestyle,
    MatchType,
    SearchType,
    Territory,
    WorkdayType,
)


class Profile(models.Model):
    user = models.OneToOneField(
        'core.User',
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
    )
    name = models.CharField('Как обращаться', max_length=128)
    gender = models.CharField('Пол', choices=Gender, max_length=20)
    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        related_name='profiles',
    )
    department = models.ForeignKey(
        'core.Department',
        on_delete=models.CASCADE,
        related_name='profiles',
    )
    interest = models.ForeignKey(
        'core.Interest',
        on_delete=models.CASCADE,
        related_name='profiles',
    )
    career_focus_direction = models.ForeignKey(
        'core.CareerFocusDirection',
        on_delete=models.CASCADE,
        related_name='profiles',
    )
    search_type = models.CharField(
        'Кого ищет',
        choices=SearchType,
        max_length=20,
    )
    match_type = models.CharField(
        choices=MatchType,
        max_length=20,
    )
    workday_type = models.CharField(
        choices=WorkdayType,
        max_length=20,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкеты'

    def __str__(self) -> str:
        return str(self.user)


class ProfileLifestyle(models.Model):
    profile = models.ForeignKey('core.Profile', on_delete=models.CASCADE)
    lifestyle = models.CharField(choices=Lifestyle, max_length=20)

    class Meta:
        unique_together = ('profile', 'lifestyle')


class City(models.Model):
    name = models.CharField('Название', unique=True, max_length=255)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self) -> str:
        return self.name


class Department(models.Model):
    name = models.CharField('Название', unique=True, max_length=255)

    class Meta:
        verbose_name = 'Департамент'
        verbose_name_plural = 'Департаменты'

    def __str__(self) -> str:
        return self.name


class Interest(models.Model):
    name = models.CharField('Название', unique=True, max_length=255)
    territory = models.CharField(
        'Территория',
        choices=Territory,
        max_length=20,
    )

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self) -> str:
        return self.name


class CareerFocusDirection(models.Model):
    name = models.CharField('Название', unique=True, max_length=255)
    career_focus = models.CharField(
        'Базовое направление',
        choices=CareerFocus,
        max_length=20,
    )

    class Meta:
        verbose_name = 'Направление в работе'
        verbose_name_plural = 'Направления в работе'

    def __str__(self) -> str:
        return self.name
