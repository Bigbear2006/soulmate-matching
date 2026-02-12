from django.contrib import admin
from django.contrib.auth.models import Group

from core.models import ContactsExchangeRequest, Match, Profile, User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin[User]):
    search_fields = ('first_name', 'last_name', 'username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin[Match]):
    list_display = ('initiator', 'recipient', 'created_at')
    ordering = ('-created_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin[Profile]):
    list_select_related = ('user',)
    readonly_fields = (
        'user',
        'created_at',
    )
    ordering = ('-created_at',)


@admin.register(ContactsExchangeRequest)
class ContactsExchangeRequestAdmin(admin.ModelAdmin[ContactsExchangeRequest]):
    list_select_related = ('match__initiator', 'match__recipient')
    list_display = ('user_1', 'user_2', 'status', 'created_at')
    list_filter = ('status',)
    ordering = ('-created_at',)

    @admin.display(description='Пользователь 1')
    def user_1(self, obj: ContactsExchangeRequest) -> str:
        return str(obj.match.initiator)

    @admin.display(description='Пользователь 2')
    def user_2(self, obj: ContactsExchangeRequest) -> str:
        return str(obj.match.recipient)
