from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_matching_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Начать',
                callback_data='start_matching',
            ),
        ],
    ],
)
