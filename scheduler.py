import json

from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from const import CONFIG_PATH

config_file = CONFIG_PATH + "/config.json"


def load_reminders():
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        return {}


def save_reminder(user_id: int, time_str: str):
    reminders = load_reminders()
    reminders[str(user_id)] = time_str
    with open(config_file, "w") as f:
        json.dump(reminders, f, indent=2)


def schedule_reminders(scheduler: AsyncIOScheduler, bot: Bot):
    reminders = load_reminders()
    for user_id, reminder_time in reminders.items():
        hour, minute = map(int, reminder_time.split(":"))

        scheduler.add_job(
            send_reminder,
            trigger='cron',
            hour=hour,
            minute=minute,
            args=[bot, int(user_id)],
            id=f"reminder_{user_id}",
            replace_existing=True,
        )


async def send_reminder(bot: Bot, user_id: int):
    await bot.send_message(
        chat_id=user_id,
        text="📝 Time to record your daily diary entry! Send me a voice note when you're ready."
    )
