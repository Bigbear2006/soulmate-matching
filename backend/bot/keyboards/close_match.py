from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

confirm_close_match_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='confirm_close_match')],
        [InlineKeyboardButton(text='Нет', callback_data='reject_close_match')],
    ],
)
