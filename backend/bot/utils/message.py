import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import Message

from bot.loader import bot, logger

_P = ParamSpec('_P')
_R = TypeVar('_R')


def handle_send_message_errors(
    send_message_func: Callable[_P, Coroutine[Any, Any, _R]],
) -> Callable[_P, Coroutine[Any, Any, _R | None]]:
    async def decorator(*args: _P.args, **kwargs: _P.kwargs) -> _R | None:
        chat_id = kwargs.get('chat_id', '?')
        try:
            return await send_message_func(*args, **kwargs)
        except TelegramRetryAfter as e:
            logger.warning(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of rate limit',
            )
            await asyncio.sleep(e.retry_after)
            return await send_message_func(*args, **kwargs)
        except TelegramAPIError as e:
            logger.warning(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of an {e.__class__.__name__} error: {str(e)}',
            )
            return None

    return decorator


@handle_send_message_errors
async def safe_send_message(
    *,
    chat_id: int | str,
    text: str,
    **kwargs: Any,
) -> Message:
    return await bot.send_message(chat_id, text, **kwargs)
