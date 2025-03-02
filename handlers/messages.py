import logging
import os
from aiogram import Dispatcher
from aiogram.enums import ParseMode, ContentType
from aiogram.types import Message

from config import MAX_FILE_SIZE, ALLOWED_EXTENSIONS, GENERATED_DIR
from database.db_manager import asave_message, aupdate_message_response, asave_error
from database.models import Message as DbMessage, Error as DbError
from services.openai_service import get_gpt_response
from services.latex_service import preprocess_response, render_latex_to_image, process_image_with_latex_ocr
from utils.text_processing import split_response, clear_splitted_response

logger = logging.getLogger(__name__)


def _cleanup(*paths: str) -> None:
    """Remove transient files, ignoring any that are already gone."""
    for path in paths:
        try:
            os.remove(path)
        except OSError:
            pass


async def process_text_response(message: Message, gpt_response: str) -> None:
    """
    Process and send a GPT response with potential LaTeX content.

    Args:
        message: The message to reply to
        gpt_response: The GPT-generated response
    """
    chunks = split_response(preprocess_response(gpt_response))
    img_index = 0

    for chunk in chunks:
        cleared_chunk = clear_splitted_response(str(chunk))
        if cleared_chunk != "" and cleared_chunk and len(cleared_chunk) != 0:
            if cleared_chunk[0] != "$":
                await message.answer(cleared_chunk, parse_mode=ParseMode.MARKDOWN)
            else:
                photo = await render_latex_to_image(cleared_chunk, message.message_id, img_index)
                try:
                    await message.answer_photo(photo=photo)
                finally:
                    _cleanup(photo.path)
                img_index += 1


async def handle_text_message(message: Message) -> None:
    """Handle text messages."""
    try:
        # Save message to database
        db_message = DbMessage(
            msg_tg_id=message.message_id,
            username=message.from_user.username,
            user_id=message.from_user.id,
            date=str(message.date),
            prompt=message.text,
        )
        await asave_message(db_message)

        # Get and process response
        gpt_response = await get_gpt_response(message.text)
        await process_text_response(message, gpt_response)

        # Update database with response
        await aupdate_message_response(message.message_id, gpt_response)

        logger.info(f"Processed text message from user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error processing text message: {e}")
        await handle_error(message, e)


async def handle_document_message(message: Message) -> None:
    """Handle document messages."""
    file_name = None
    try:
        document = message.document
        file_size = (document.file_size or 0) / (1024 * 1024)

        if file_size > MAX_FILE_SIZE:
            await message.answer(
                f"Розмір вашого файлу занадто великий. Максимальний дозволений розмір - {MAX_FILE_SIZE} MB.")
            return

        extension = document.file_name.split('.')[-1]
        if extension not in ALLOWED_EXTENSIONS:
            raise TypeError(f"Unsupported file extension: {extension}")

        file_path = (await message.bot.get_file(document.file_id)).file_path
        os.makedirs(GENERATED_DIR, exist_ok=True)
        file_name = os.path.join(GENERATED_DIR, f"{message.message_id}.{extension}")
        await message.bot.download_file(file_path, file_name)

        with open(file_name, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Save message to database
        db_message = DbMessage(
            msg_tg_id=message.message_id,
            username=message.from_user.username,
            user_id=message.from_user.id,
            date=str(message.date),
            prompt=f"{message.text or ''}\n[FILE: {document.file_name}]",
        )
        await asave_message(db_message)

        # Get and process response
        if message.text:
            gpt_response = await get_gpt_response(message.text + "\n\n" + file_content)
        else:
            gpt_response = await get_gpt_response(file_content)

        await process_text_response(message, gpt_response)

        # Update database with response
        await aupdate_message_response(message.message_id, gpt_response)

        logger.info(f"Processed document message from user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error processing document message: {e}")
        await handle_error(message, e)
    finally:
        if file_name:
            _cleanup(file_name)


async def handle_photo_message(message: Message) -> None:
    """Handle photo messages."""
    file_name = None
    try:
        photo = message.photo[-1]
        file_size = (photo.file_size or 0) / (1024 * 1024)

        if file_size > MAX_FILE_SIZE:
            await message.answer(
                f"Розмір вашого фото занадто великий. Максимальний дозволений розмір - {MAX_FILE_SIZE} MB.")
            return

        file_path = (await message.bot.get_file(photo.file_id)).file_path
        os.makedirs(GENERATED_DIR, exist_ok=True)
        file_name = os.path.join(GENERATED_DIR, f"in{message.message_id}.png")
        await message.bot.download_file(file_path, file_name)

        # Process image with LaTeX OCR
        photo_content = await process_image_with_latex_ocr(file_name)

        # Save message to database
        db_message = DbMessage(
            msg_tg_id=message.message_id,
            username=message.from_user.username,
            user_id=message.from_user.id,
            date=str(message.date),
            prompt=f"{message.caption or ''}\n[IMAGE: LaTeX content detected: {photo_content}]",
        )
        await asave_message(db_message)

        # Get and process response
        if message.caption:
            prompt = photo_content + ' ' + message.caption
            gpt_response = await get_gpt_response(prompt)
        else:
            gpt_response = await get_gpt_response(photo_content)

        await process_text_response(message, gpt_response)

        # Update database with response
        await aupdate_message_response(message.message_id, gpt_response)

        logger.info(f"Processed photo message from user {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error processing photo message: {e}")
        await handle_error(message, e)
    finally:
        if file_name:
            _cleanup(file_name)


async def handle_error(message: Message, exception: Exception) -> None:
    """Handle and log errors."""
    try:
        if isinstance(exception, TypeError):
            await message.answer(
                "Формат вашого повідомлення не підтримується. На даний момент, енциклопедія приймає лише текстові запити.")
        else:
            await message.answer("Дуже прикро, але під час опрацювання вашого запиту сталася помилка.")

        # Save error to database
        error = DbError(
            msg_tg_id=message.message_id,
            error_text=str(exception)
        )
        await asave_error(error)
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


async def echo_handler(message: Message) -> None:
    """Main message handler that routes to specific handlers based on content type."""
    try:
        if message.content_type == ContentType.TEXT:
            await handle_text_message(message)
        elif message.content_type == ContentType.DOCUMENT:
            await handle_document_message(message)
        elif message.content_type == ContentType.PHOTO:
            await handle_photo_message(message)
        else:
            raise TypeError(f"Unsupported content type: {message.content_type}")
    except Exception as e:
        logger.error(f"Error in echo handler: {e}")
        await handle_error(message, e)


def register_message_handlers(dp: Dispatcher) -> None:
    """Register message handlers with the dispatcher."""
    dp.message.register(echo_handler)