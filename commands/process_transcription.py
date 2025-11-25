import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from button_helper import send_file_buttons
from const import TRANSCRIPTION_DIR
from processes import transcribed_file_to_diary


async def send_transcription_buttons(update_or_query, user_id, page: int):
    user_transcription_directory = os.path.join(TRANSCRIPTION_DIR, str(user_id))

    await send_file_buttons(update_or_query=update_or_query,
                            prompt="Select a transcription file to process (latest first):",
                            file_emoji="📄",
                            directory=user_transcription_directory,
                            callback_prefix="transcription",
                            page=page)


async def process_transcription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await send_transcription_buttons(update, user_id, 1)


async def handle_transcription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    prefix, filename = data.split("|", 1)

    path = os.path.join(TRANSCRIPTION_DIR, user_id, filename)
    if not os.path.exists(path):
        await query.edit_message_text("❌ File not found.")
        return

    await transcribed_file_to_diary(query.message, audio_path=None, transcription_path=path)