from aiogram import F, Router, flags
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.callback_data import IntDetailActionCallback
from bot.filters import action_filter
from bot.keyboards.exchange_contacts import (
    accept_exchange_contacts_request_kb,
    confirm_exchange_contacts_kb,
)
from bot.services.matching import get_soulmate
from bot.types import expect
from core.models import ContactsExchangeRequest, User

router = Router()


@router.message(Command('exchange_contacts'))
async def exchange_contacts_handler(msg: Message) -> None:
    if not msg.message_thread_id:
        await msg.answer('Отправляйте сообщение в тему')
        return

    soulmate = await get_soulmate(msg.message_thread_id)
    await msg.answer(
        f'Вы хотите обменяться контактами с {soulmate.user.profile.name}?',
        reply_markup=confirm_exchange_contacts_kb,
    )


@router.callback_query(F.data == 'confirm_exchange_contacts')
@flags.user
async def confirm_exchange_contacts_handler(
    query: CallbackQuery,
    user: User,
) -> None:
    soulmate = await get_soulmate(expect(query.message.message_thread_id))
    exchange_request = await ContactsExchangeRequest.objects.acreate(
        match=soulmate.match,
        created_by=user,
    )
    await query.bot.send_message(
        soulmate.user.id,
        text=f'Хочешь обменяться контактами с {user.profile.name}?',
        reply_markup=accept_exchange_contacts_request_kb(exchange_request.pk),
        message_thread_id=soulmate.thread_id,
    )
    await query.message.edit_text(
        'Запрос на обмен контактами отправлен. '
        'Бот пришлет уведомление, когда пользователь ответит',
    )


@router.callback_query(F.data == 'cancel_exchange_contacts')
async def cancel_exchange_contacts_handler(query: CallbackQuery) -> None:
    await query.message.edit_text('Вы отменили обмен контактами')


@router.callback_query(
    action_filter('exchange_contacts_request', 'accept', detail=True),
)
@flags.user
async def accept_exchange_contacts_request_handler(
    query: CallbackQuery,
    callback_data: IntDetailActionCallback,
    user: User,
) -> None:
    soulmate = await get_soulmate(expect(query.message.message_thread_id))
    await query.message.edit_text(f'Твой собеседник - {soulmate.user}')
    await query.bot.send_message(
        soulmate.user.id,
        text=f'Твой собеседник {user.profile.name}?',
        message_thread_id=soulmate.thread_id,
    )
    await ContactsExchangeRequest.objects.accept(callback_data.pk)


@router.callback_query(
    action_filter('exchange_contacts_request', 'decline', detail=True),
)
async def decline_exchange_contacts_request_handler(
    query: CallbackQuery,
    callback_data: IntDetailActionCallback,
) -> None:
    soulmate = await get_soulmate(expect(query.message.message_thread_id))
    await query.bot.send_message(
        soulmate.user.id,
        text='Собеседник отклонил заявку на обмен контактами',
        message_thread_id=soulmate.thread_id,
    )
    await query.message.edit_text('Вы отклонили запрос на обмен контактами')
    await ContactsExchangeRequest.objects.decline(callback_data.pk)
