from telegram import Update
from telegram.ext import ContextTypes

from commands.process_audio import handle_audio_callback
from commands.process_transcription import handle_transcription_callback


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    prefix, filename = data.split("|", 1)

    if prefix == "process_audio":
        await handle_audio_callback(update, context)
    elif prefix == "process_transcription":
        await handle_transcription_callback(update, context)