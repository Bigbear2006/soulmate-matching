from typing import TYPE_CHECKING

from aiogram import types
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from core.managers.base import BaseManager

if TYPE_CHECKING:
    from core.models import User


class UserManager(BaseManager['User']):
    def get_queryset(self) -> QuerySet['User']:
        return super().get_queryset().select_related('profile')

    async def from_tg_user(self, tg_user: types.User) -> 'User':
        return await self.acreate(
            id=tg_user.id,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            username=tg_user.username,
            is_premium=tg_user.is_premium or False,
        )

    async def update_from_tg_user(self, tg_user: types.User) -> None:
        await self.filter(pk=tg_user.id).aupdate(
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            username=tg_user.username,
            is_premium=tg_user.is_premium or False,
        )

    async def create_or_update(
        self,
        tg_user: types.User,
    ) -> tuple['User', bool]:
        try:
            user = await self.aget(pk=tg_user.id)
            await self.update_from_tg_user(tg_user)
            await user.arefresh_from_db()
            return user, False
        except ObjectDoesNotExist:
            return await self.from_tg_user(tg_user), True
