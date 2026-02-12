from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callback_data import pack_action_data

confirm_exchange_contacts_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data='confirm_exchange_contacts',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Нет',
                callback_data='cancel_exchange_contacts',
            ),
        ],
    ],
)


def accept_exchange_contacts_request_kb(
    request_id: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Согласиться',
                    callback_data=pack_action_data(
                        'exchange_contacts_request',
                        'accept',
                        request_id,
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Отклонить',
                    callback_data=pack_action_data(
                        'exchange_contacts_request',
                        'decline',
                        request_id,
                    ),
                ),
            ],
        ],
    )
