import datetime
import os

from telegram import Update
from telegram.ext import ContextTypes

from const import CONFIG_PATH
from diary_writer import generate_diary_entry, set_user_style, get_user_style
from scheduler import save_reminder, schedule_reminders
from transcribe import transcribe_voice

AUDIO_DIR = CONFIG_PATH + "/audio"
TRANSCRIPTION_DIR = CONFIG_PATH + "/transcriptions"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Send me a voice note when you're ready.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    user_id = update.effective_user.id

    now = datetime.datetime.now()
    timestamp = int(now.timestamp())
    formatted_date = now.strftime("%d_%m_%Y_%H_%M")

    audio_filename = f"{formatted_date}_{timestamp}.ogg"
    transcription_filename = f"{formatted_date}_{timestamp}.txt"

    path = os.path.join(AUDIO_DIR, str(user_id), audio_filename)
    transcription_path = os.path.join(TRANSCRIPTION_DIR, str(user_id), transcription_filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    os.makedirs(os.path.dirname(transcription_path), exist_ok=True)

    await file.download_to_drive(path)

    await update.message.reply_text("Transcribing...")
    text = transcribe_voice(path)

    # Save transcription to file
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Send the transcription text file
    await update.message.reply_document(document=open(transcription_path, "rb"), filename=transcription_filename,
                                        caption="📝 Here's your transcription")

    await update.message.reply_text("Converting to diary entry...")
    user_id = update.effective_user.id
    diary = generate_diary_entry(text, user_id)

    await update.message.reply_text(f"📔 Your entry:")
    await update.message.reply_text(diary)


async def setstyle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please include your diary style sample.\nUsage:\n`/setstyle <your sample diary entry>`",
            parse_mode="Markdown"
        )
        return

    user_id = update.effective_user.id
    style_text = " ".join(context.args)
    set_user_style(user_id, style_text)
    await update.message.reply_text("✅ Your diary style has been saved!")


def is_valid_time_format(time_str: str):
    try:
        hour, minute = map(int, time_str.split(":"))
        return 0 <= hour < 24 and 0 <= minute < 60
    except:
        return False


async def setreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⏰ Usage: /setreminder HH:MM (24-hour format)")
        return

    time_str = context.args[0]
    if not is_valid_time_format(time_str):
        await update.message.reply_text("❌ Invalid time format. Use HH:MM in 24-hour format.")
        return

    user_id = update.effective_user.id
    save_reminder(user_id, time_str)

    # Reschedule this user's job
    schedule_reminders(context.application.job_queue.scheduler, context.bot)

    await update.message.reply_text(f"✅ Your daily reminder is set for {time_str}.")


async def getstyle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    style = get_user_style(user_id)

    await update.message.reply_text(f"{style}")