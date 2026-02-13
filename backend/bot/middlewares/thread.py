from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, TelegramObject


class MessageThreadMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not get_flag(data, 'thread'):
            return await handler(event, data)

        if not isinstance(event, Message):
            return await handler(event, data)

        thread_id = event.message_thread_id
        if not thread_id:
            await event.answer('Отправляйте сообщение в тему')
            return None

        data['thread_id'] = thread_id
        return await handler(event, data)
