from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

from core.models import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.chat.id
        elif isinstance(event, CallbackQuery):
            user_id = event.message.chat.id
        else:
            return await handler(event, data)

        user_flag = get_flag(data, 'user')
        if user_flag:
            user = await User.objects.aget(pk=user_id)
            data['user'] = user

        data['user_id'] = user_id
        return await handler(event, data)
