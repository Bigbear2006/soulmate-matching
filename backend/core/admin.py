from django.contrib import admin
from django.contrib.auth.models import Group

from core.models import (
    Answer,
    ContactsExchangeRequest,
    Match,
    Profile,
    ProfileAnswer,
    ProfileInterest,
    ProfileLifestyle,
    Question,
    User,
)

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin[User]):
    search_fields = ('first_name', 'last_name', 'username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    group = 'Основное'


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin[Match]):
    list_display = ('initiator', 'recipient', 'created_at')
    ordering = ('-created_at',)
    group = 'Основное'


class ProfileAnswerInline(admin.TabularInline[ProfileAnswer, Profile]):
    model = ProfileAnswer
    readonly_fields = ('answer',)
    extra = 0


class ProfileLifestyleInline(admin.TabularInline[ProfileLifestyle, Profile]):
    model = ProfileLifestyle
    readonly_fields = ('lifestyle',)
    extra = 0


class ProfileInterestInline(admin.TabularInline[ProfileInterest, Profile]):
    model = ProfileInterest
    readonly_fields = ('interest',)
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin[Profile]):
    list_select_related = ('user',)
    readonly_fields = ('user', 'created_at')
    inlines = (
        ProfileAnswerInline,
        ProfileLifestyleInline,
        ProfileInterestInline,
    )
    ordering = ('-created_at',)
    group = 'Основное'


@admin.register(ContactsExchangeRequest)
class ContactsExchangeRequestAdmin(admin.ModelAdmin[ContactsExchangeRequest]):
    list_select_related = ('match__initiator', 'match__recipient')
    list_display = ('user_1', 'user_2', 'status', 'created_at')
    list_filter = ('status',)
    ordering = ('-created_at',)
    group = 'Основное'

    @admin.display(description='Пользователь 1')
    def user_1(self, obj: ContactsExchangeRequest) -> str:
        return str(obj.match.initiator)

    @admin.display(description='Пользователь 2')
    def user_2(self, obj: ContactsExchangeRequest) -> str:
        return str(obj.match.recipient)


class AnswerInline(admin.StackedInline[Answer, Question]):
    model = Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin[Question]):
    exclude = ('key',)
    inlines = (AnswerInline,)
    ordering = ('order',)
    group = 'Вопросы'
