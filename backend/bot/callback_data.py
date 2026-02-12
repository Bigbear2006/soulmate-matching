from typing import Final, TypeVar

from aiogram.filters.callback_data import CallbackData

ACTION_PREFIX: Final[str] = 'action'

_PK = TypeVar('_PK', default=int)


class ActionCallback(CallbackData, prefix=ACTION_PREFIX):
    model: str
    action: str


class IntDetailActionCallback(ActionCallback, prefix=ACTION_PREFIX):
    pk: int


class StrDetailActionCallback(ActionCallback, prefix=ACTION_PREFIX):
    pk: str


def pack_action_data(model: str, action: str, pk: _PK | None = None) -> str:
    if not pk:
        return ActionCallback(model=model, action=action).pack()

    if isinstance(pk, int):
        return IntDetailActionCallback(
            model=model,
            action=action,
            pk=pk,
        ).pack()
    elif isinstance(pk, str):
        return StrDetailActionCallback(
            model=model,
            action=action,
            pk=pk,
        ).pack()

    raise TypeError(f'Got {type(pk)}, but only int or str pk are supported')
