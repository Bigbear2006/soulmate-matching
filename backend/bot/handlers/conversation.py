from aiogram import F, Router
from aiogram.types import Message

from bot.services.matching import get_soulmate

router = Router()


@router.message(F)
async def forward_message_handler(msg: Message) -> None:
    if not msg.message_thread_id:
        await msg.answer('Отправляйте сообщение в тему')
        return

    soulmate = await get_soulmate(msg.message_thread_id)
    await msg.send_copy(soulmate.user.id, message_thread_id=soulmate.thread_id)
