from collections.abc import Callable
from typing import TypeVar

from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message

from bot.types import expect

_R = TypeVar('_R')


async def validate_message(
    msg: Message,
    *,
    func: Callable[[str], _R],
    fail_text: str,
    exceptions: type[Exception] | tuple[type[Exception], ...] = ValueError,
) -> _R:
    try:
        return func(expect(msg.text))
    except exceptions:
        await msg.answer(fail_text)
        raise SkipHandler from None
