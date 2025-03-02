import logging
from aiogram import Dispatcher, html
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)

async def command_start_handler(message: Message) -> None:
    """Handle the /start command."""
    try:
        await message.answer(f"Вітаю, пірате {html.bold(message.from_user.full_name)}! Готовий дати відповідь на будь-яке твоє питання!")
        logger.info(f"User {message.from_user.id} started the bot")
    except Exception as e:
        logger.error(f"Error in start command handler: {e}")

def register_command_handlers(dp: Dispatcher) -> None:
    """Register command handlers with the dispatcher."""
    dp.message.register(command_start_handler, CommandStart())