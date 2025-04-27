import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.commands import router as commands_router
from handlers.menu import router as menu_router
from handlers.theory import router as theory_router
from data.database import init_db
from handlers.tests import router as tests_router
from handlers.practice import router as practice_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

async def main():
    try:
        bot = Bot(token="your_token")  #токен
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация роутеров
        dp.include_router(commands_router)
        dp.include_router(menu_router)
        dp.include_router(theory_router)
        dp.include_router(tests_router)
        dp.include_router(practice_router)

        # Инициализация БД
        await init_db()

        logging.info("Бот запущен")
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        if 'bot' in locals():
            await bot.close()
        logging.info("Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())

