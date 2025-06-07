import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from handlers import start, handle_voice, setstyle, setreminder, getstyle
from scheduler import schedule_reminders


async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("setstyle", "Set your diary style"),
        BotCommand("setreminder", "Set daily reminder time"),
        BotCommand("getstyle", "Retrieve the style you have set for the bot")
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

system_timezone = datetime.now().astimezone().tzinfo
scheduler = AsyncIOScheduler(timezone=system_timezone)
scheduler.start()
schedule_reminders(scheduler, app.bot)

print("Bot started.")

app.run_polling()
