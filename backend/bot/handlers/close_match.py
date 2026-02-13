from aiogram import F, Router, flags
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.close_match import confirm_close_match_kb
from bot.services.matching import get_soulmate
from bot.types import expect
from core.models import Match, User

router = Router()


@router.message(Command('close_match'))
@flags.thread
async def close_match_handler(msg: Message, thread_id: int) -> None:
    soulmate = await get_soulmate(thread_id)
    await msg.answer(
        f'Ты точно хочешь завершить диалог с {soulmate}?',
        reply_markup=confirm_close_match_kb,
    )


@router.callback_query(F.data == 'confirm_close_match')
@flags.user
async def confirm_close_match_handler(
    query: CallbackQuery,
    user: User,
) -> None:
    thread_id = expect(query.message.message_thread_id)
    soulmate = await get_soulmate(thread_id)
    await query.bot.delete_forum_topic(query.message.chat.id, thread_id)
    await query.bot.delete_forum_topic(soulmate.user.pk, soulmate.thread_id)
    await Match.objects.close(soulmate.match.pk)

    await query.message.edit_text(f'Ты завершил диалог с {soulmate}')
    await query.bot.send_message(
        soulmate.user.pk,
        f'Пользователь {user.profile.name} завершил диалог',
    )


@router.callback_query(F.data == 'reject_close_match')
async def reject_close_match_handler(query: CallbackQuery) -> None:
    thread_id = expect(query.message.message_thread_id)
    soulmate = await get_soulmate(thread_id)
    await query.message.edit_text(f'Завершение диалога с {soulmate} отменено')
