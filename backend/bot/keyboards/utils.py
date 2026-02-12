from collections.abc import Callable
from typing import Any, cast

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Choices, QuerySet


def one_button_keyboard(
    *,
    back_button_data: str | None = None,
    **kwargs: Any,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(**kwargs)
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    return cast(InlineKeyboardMarkup, kb.adjust(1).as_markup())


def keyboard_from_choices(
    choices: type[Choices],
    *,
    prefix: str = '',
    back_button_data: str | None = None,
    width: int = 1,
    only: list[Choices] | None = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for value, label in choices.choices:
        if only and value not in only:
            continue
        kb.button(
            text=label,
            callback_data=f'{prefix}:{value}' if prefix else str(value),
        )
    if back_button_data:
        kb.button(text='В меню', callback_data=back_button_data)
    return cast(InlineKeyboardMarkup, kb.adjust(width).as_markup())


async def get_pagination_buttons(
    previous_button_data: str = '',
    next_button_data: str = '',
) -> list[InlineKeyboardButton]:
    pagination_buttons = []

    if previous_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='<-',
                callback_data=previous_button_data,
            ),
        )

    if next_button_data:
        pagination_buttons.append(
            InlineKeyboardButton(text='->', callback_data=next_button_data),
        )

    return pagination_buttons


async def keyboard_from_queryset(
    queryset: QuerySet[Any],
    prefix: str,
    *,
    str_func: Callable[[Any], str] = str,
    back_button_text: str = 'Назад',
    back_button_data: str = '',
    previous_button_data: str = '',
    next_button_data: str = '',
    width: int = 1,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    async for obj in queryset:
        kb.button(text=str_func(obj), callback_data=f'{prefix}:{obj.pk}')

    if back_button_data:
        kb.button(text=back_button_text, callback_data=back_button_data)

    kb.row(
        *await get_pagination_buttons(previous_button_data, next_button_data),
    )
    return cast(InlineKeyboardMarkup, kb.adjust(width).as_markup())


async def get_paginated_keyboard(
    queryset: QuerySet[Any],
    prefix: str = '',
    *,
    str_func: Callable[[Any], str] = str,
    page: int = 1,
    page_size: int = 5,
    back_button_data: str = '',
    previous_button_data: str = '',
    next_button_data: str = '',
) -> InlineKeyboardMarkup:
    total_count = await queryset.acount()
    total_pages = (total_count + page_size - 1) // page_size
    start, end = (page - 1) * page_size, page * page_size
    return await keyboard_from_queryset(
        queryset[start:end],
        prefix=prefix,
        str_func=str_func,
        back_button_data=back_button_data,
        previous_button_data=previous_button_data if page > 1 else '',
        next_button_data=next_button_data if page < total_pages else '',
    )
