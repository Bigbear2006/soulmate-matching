from aiogram import F
from aiogram.filters.callback_data import CallbackQueryFilter

from bot.callback_data import (
    ActionCallback,
    IntDetailActionCallback,
    StrDetailActionCallback,
)


def get_action_callback_class(
    *,
    detail: bool,
    pk_type: type,
) -> type[ActionCallback]:
    if not detail:
        return ActionCallback

    if issubclass(pk_type, int):
        return IntDetailActionCallback
    if issubclass(pk_type, str):
        return StrDetailActionCallback

    raise TypeError(f'Got {pk_type}, but only int or str pk are supported')


def action_filter(
    model: str,
    *actions: str,
    detail: bool = False,
    pk_type: type = int,
) -> CallbackQueryFilter:
    cls = get_action_callback_class(detail=detail, pk_type=pk_type)
    return cls.filter((F.model == model) & (F.action.in_(actions)))
