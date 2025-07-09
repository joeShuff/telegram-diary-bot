import os

from telegram import Update
from telegram.ext import ContextTypes

from button_helper import send_file_buttons
from const import AUDIO_DIR
from processes import audio_file_to_diary


async def send_audio_buttons(update_or_query, user_id, page: int):
    user_audio_directory = os.path.join(AUDIO_DIR, str(user_id))

    await send_file_buttons(update_or_query,
                            prompt="Select an audio file to process (latest first):",
                            file_emoji="🎧",
                            directory=user_audio_directory,
                            callback_prefix="audio",
                            page=page)


async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await send_audio_buttons(update, user_id, 1)


async def handle_audio_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    prefix, filename = data.split("|", 1)

    path = os.path.join(AUDIO_DIR, user_id, filename)
    if not os.path.exists(path):
        await query.edit_message_text("❌ File not found.")
        return

    await audio_file_to_diary(query.message, path)
