import asyncio
from aiogram import Bot, Dispatcher
from handlers.start_page_handlers import router as start_page_router
from handlers.admin_handlers import router as admin_router
from handlers.handlers import router as general_router
from config import config
from utils.scheduler import scheduler_setup


async def main():
    bot = Bot(token=config.API_TOKEN)
    dp = Dispatcher()
    dp.include_router(start_page_router)
    dp.include_router(admin_router)
    dp.include_router(general_router)

    scheduler_setup()

    await dp.start_polling(bot)


asyncio.run(main())