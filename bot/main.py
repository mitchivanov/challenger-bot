import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TG_TOKEN
from handlers import challenges

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Starting bot...")
        bot = Bot(token=TG_TOKEN, parse_mode='HTML')
        dp = Dispatcher()
        
        # Подключаем роутеры
        dp.include_router(challenges.router)
        logger.info("All routers included successfully")
        
        logger.info("Bot started successfully, starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
