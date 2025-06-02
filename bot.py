import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from const import CONFIG_PATH
from handlers import start, handle_voice, setstyle, setreminder
from scheduler import schedule_reminders

# Create config folder
os.makedirs(CONFIG_PATH, exist_ok=True)

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VOICE, handle_voice))
app.add_handler(CommandHandler("setstyle", setstyle))
app.add_handler(CommandHandler("setreminder", setreminder))

scheduler = AsyncIOScheduler()
scheduler.start()
schedule_reminders(scheduler, app.bot)

print("Bot started.")

app.run_polling()