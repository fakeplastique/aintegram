from aiogram import Dispatcher
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers

def register_all_handlers(dp: Dispatcher) -> None:
    """Register all handlers with the dispatcher."""
    register_command_handlers(dp)
    register_message_handlers(dp)