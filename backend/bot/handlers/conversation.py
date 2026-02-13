from aiogram import F, Router, flags
from aiogram.types import Message
from django.core.exceptions import ObjectDoesNotExist

from bot.services.matching import get_soulmate

router = Router()


@router.message(F)
@flags.thread
async def forward_message_handler(msg: Message, thread_id: int) -> None:
    try:
        soulmate = await get_soulmate(thread_id)
    except ObjectDoesNotExist:
        await msg.answer('Мэтч не найден')
        return

    await msg.send_copy(soulmate.user.id, message_thread_id=soulmate.thread_id)
