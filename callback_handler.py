from telegram import Update
from telegram.ext import ContextTypes

from commands.process_audio import handle_audio_callback, send_audio_buttons
from commands.process_transcription import handle_transcription_callback, send_transcription_buttons


async def handle_audio_process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    prefix, extra = data.split("|", 1)

    if prefix == "audio_process":
        await query.edit_message_text(f"🎧 Processing audio: `{extra}`", parse_mode="Markdown")
        await handle_audio_callback(update, context)


async def handle_transcription_process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    prefix, extra = data.split("|", 1)

    if prefix == "transcription_process":
        await query.edit_message_text(f"📄 Processing transcription: `{extra}`", parse_mode="Markdown")
        await handle_transcription_callback(update, context)


async def handle_audio_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    prefix, extra = data.split("|", 1)

    if prefix == "audio_page":
        page = int(extra)
        await send_audio_buttons(query, query.from_user.id, page)


async def handle_transcription_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    prefix, extra = data.split("|", 1)

    if prefix == "transcription_page":
        page = int(extra)
        await send_transcription_buttons(query, query.from_user.id, page)
