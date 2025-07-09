import os

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from const import AUDIO_DIR
from processes import audio_file_to_diary


async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_audio_dir = os.path.join(AUDIO_DIR, user_id)

    if not os.path.exists(user_audio_dir):
        await update.message.reply_text("❌ No audio files found.")
        return

    files = [
        f for f in os.listdir(user_audio_dir)
        if f.endswith(".ogg") or f.endswith(".mp3")
    ]

    # Sort files by timestamp in descending order (latest first)
    def extract_timestamp(filename):
        try:
            return int(filename.rsplit("_", 1)[-1].split(".")[0])
        except ValueError:
            return 0  # fallback if filename format is off

    files.sort(key=extract_timestamp, reverse=True)

    if not files:
        await update.message.reply_text("❌ No audio files found.")
        return

    keyboard = [
        [InlineKeyboardButton(f"🎧 {file}", callback_data=f"process_audio|{file}")]
        for file in files
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select an audio file to process (latest first):",
        reply_markup=reply_markup
    )


async def handle_audio_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    prefix, filename = data.split("|", 1)

    if prefix != "process_audio":
        return  # Ignore unrelated buttons

    path = os.path.join(AUDIO_DIR, user_id, filename)
    if not os.path.exists(path):
        await query.edit_message_text("❌ File not found.")
        return

    await audio_file_to_diary(query.message, path)