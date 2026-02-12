import os

import django
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger, loop


async def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import conversation, exchange_contacts, registration
    from bot.middlewares import UserMiddleware, setup_middlewares

    dp.include_routers(
        registration.router,
        exchange_contacts.router,
        conversation.router,
    )
    setup_middlewares(dp, UserMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
            BotCommand(
                command='/exchange_contacts',
                description='Обменяться контактами',
            ),
        ],
    )

    me = await bot.get_me()
    logger.info(f'Starting bot @{me.username}...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
