from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import QuerySet, Window
from django.db.models.functions import RowNumber

from bot.callback_data import pack_action_data
from bot.keyboards.utils import keyboard_from_choices, keyboard_from_queryset
from core.choices import (
    CareerFocus,
    Gender,
    Lifestyle,
    MatchType,
    SearchType,
    Territory,
    WorkdayType,
)
from core.models import (
    Answer,
    CareerFocusDirection,
    City,
    Department,
    Interest,
)


def get_genders_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(Gender, prefix='gender')


async def get_cities_kb() -> InlineKeyboardMarkup:
    return await keyboard_from_queryset(
        City.objects.all(),
        pack_action_data('city', 'select'),
    )


async def get_departments_kb() -> InlineKeyboardMarkup:
    return await keyboard_from_queryset(
        Department.objects.annotate(
            number=Window(expression=RowNumber(), order_by='id'),
        ).all(),
        pack_action_data('department', 'select'),
        str_func=lambda d: str(d.number),
        width=2,
    )


def get_lifestyles_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder.from_markup(
        keyboard_from_choices(Lifestyle, prefix='lifestyle'),
    )
    kb.row(
        InlineKeyboardButton(text='Готово', callback_data='lifestyle:done'),
    )
    return kb.as_markup()


def get_territories_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(Territory, prefix='territory')


async def get_interests_kb(territory: Territory | str) -> InlineKeyboardMarkup:
    return await keyboard_from_queryset(
        Interest.objects.filter(territory=territory),
        pack_action_data('interest', 'select'),
    )


def get_career_focuses_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(CareerFocus, prefix='career_focus')


async def get_career_focus_directions_kb(
    career_focus: CareerFocus | str,
) -> InlineKeyboardMarkup:
    return await keyboard_from_queryset(
        CareerFocusDirection.objects.filter(career_focus=career_focus),
        prefix=pack_action_data('career_focus_direction', 'select'),
    )


def get_answers_kb(answers: QuerySet[Answer]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=answer.text,
                    callback_data=pack_action_data(
                        'answer',
                        'select',
                        answer.pk,
                    ),
                ),
            ]
            for answer in answers
        ],
    )


def get_search_types_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(SearchType, prefix='search_type')


def get_match_types_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(MatchType, prefix='match_type')


def get_workday_types_kb() -> InlineKeyboardMarkup:
    return keyboard_from_choices(WorkdayType, prefix='workday_type')
