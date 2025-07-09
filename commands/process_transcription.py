import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from const import TRANSCRIPTION_DIR
from processes import transcribed_file_to_diary


async def process_transcription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_transcription_dir = os.path.join(TRANSCRIPTION_DIR, user_id)

    if not os.path.exists(user_transcription_dir):
        await update.message.reply_text("❌ No audio files found.")
        return

    files = [
        f for f in os.listdir(user_transcription_dir)
        if f.endswith(".txt")
    ]

    # Sort files by timestamp in descending order (latest first)
    def extract_timestamp(filename):
        try:
            return int(filename.rsplit("_", 1)[-1].split(".")[0])
        except ValueError:
            return 0  # fallback if filename format is off

    files.sort(key=extract_timestamp, reverse=True)

    if not files:
        await update.message.reply_text("❌ No transcription files found.")
        return

    keyboard = [
        [InlineKeyboardButton(f"📄 {file}", callback_data=f"process_transcription|{file}")]
        for file in files
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Select a transcription file to process (latest first):",
        reply_markup=reply_markup
    )


async def handle_transcription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    prefix, filename = data.split("|", 1)

    if prefix != "process_transcription":
        return  # Ignore unrelated buttons

    path = os.path.join(TRANSCRIPTION_DIR, user_id, filename)
    if not os.path.exists(path):
        await query.edit_message_text("❌ File not found.")
        return

    await transcribed_file_to_diary(query.message, path)