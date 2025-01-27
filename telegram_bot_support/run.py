import asyncio
from aiogram import Bot, Dispatcher, F

from handlers.handler_1 import router
from handlers.callback_1 import router_callbacks
from handlers.admin_handler import admin_router
from config import TOKEN
from database.models_db import db_run
from database import models_db as db

bot = Bot(TOKEN)
dp = Dispatcher()

async def main():
    try:
        await db_run()
        dp.include_router(admin_router)
        dp.include_router(router)
        dp.include_router(router_callbacks)
        await dp.start_polling(bot)
    finally:
        db.db.close()

if __name__ == '__main__':
    print('Bot On')
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print('Bot Off')