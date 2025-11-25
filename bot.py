import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

import plugin_core
from callback_handler import handle_audio_process_callback, handle_transcription_process_callback, \
    handle_audio_page_callback, handle_transcription_page_callback
from commands.process_audio import process_audio
from commands.process_transcription import process_transcription
from config import TELEGRAM_TOKEN
from handlers import start, handle_voice, setstyle, setreminder, getstyle
from scheduler import schedule_reminders


async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("setstyle", "Set your diary style"),
        BotCommand("setreminder", "Set daily reminder time"),
        BotCommand("getstyle", "Retrieve the style you have set for the bot"),
        BotCommand("processaudio", "Process an already send audio file. Used as backup"),
        BotCommand("processtranscription", "Process an already existing transcription. Used as backup")
    ]
    await application.bot.set_my_commands(commands)


# Create config folder
CONFIG_FOLDER = os.getcwd() + "/config"
os.makedirs(CONFIG_FOLDER, exist_ok=True)

app = Application.builder().token(TELEGRAM_TOKEN).post_init(set_bot_commands).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CommandHandler("setstyle", setstyle))
app.add_handler(CommandHandler("setreminder", setreminder))
app.add_handler(CommandHandler("getstyle", getstyle))
app.add_handler(CommandHandler("processaudio", process_audio))
app.add_handler(CallbackQueryHandler(handle_audio_process_callback, pattern="^audio_process"))
app.add_handler(CallbackQueryHandler(handle_transcription_process_callback, pattern="^transcription_process"))
app.add_handler(CallbackQueryHandler(handle_audio_page_callback, pattern="^audio_page"))
app.add_handler(CallbackQueryHandler(handle_transcription_page_callback, pattern="^transcription_page"))
app.add_handler(CommandHandler("processtranscription", process_transcription))

plugin_core.load_plugins(app)

system_timezone = datetime.now().astimezone().tzinfo
scheduler = AsyncIOScheduler(timezone=system_timezone)
scheduler.start()
schedule_reminders(scheduler, app.bot)

print("Bot started.")

app.run_polling()
