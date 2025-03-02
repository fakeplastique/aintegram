#!/usr/bin/env python3
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN, LOG_LEVEL
from database.db_manager import init_db, close_connection
from handlers import register_all_handlers


async def main() -> None:
    """Initialize and start the bot."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

    # Initialize database
    init_db()

    # Initialize Bot with default properties
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Initialize dispatcher
    dp = Dispatcher()

    # Register all handlers
    register_all_handlers(dp)

    try:
        # Start polling
        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        # Close database connection
        close_connection()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())