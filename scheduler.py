import json
from pathlib import Path
from typing import Dict

from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import user_config
from const import CONFIG_PATH
from user_config import UserConfig

config_file = Path(CONFIG_PATH + "/config.json")


def migrate_reminders():
    if not config_file.exists():
        return

    try:
        with config_file.open("r") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        print("Config file corrupted or invalid JSON — skipping migration.")
        return

    for user_id_str, reminder_time in raw.items():
        try:
            user_id = int(user_id_str)
        except ValueError:
            print(f"Skipping invalid user id key: {user_id_str}")
            continue

        # Store user config
        new_config = UserConfig(
            ai_enabled=True,
            reminder_time=reminder_time
        )
        user_config.save_user_config(user_id, new_config)

    # Delete the old file
    try:
        config_file.unlink()
        print("Old reminder config file deleted.")
    except Exception as e:
        print(f"Failed to delete old reminder file: {e}")

    print("Reminders migrated successfully.")


def load_reminders() -> dict[int, UserConfig]:
    ## To migrate from old storage to new user config
    migrate_reminders()

    return user_config.load_all_configs()


def save_reminder(user_id: int, time_str: str):
    reminders = load_reminders()
    reminders[user_id].reminder_time = time_str

    user_config.save_user_config(user_id, reminders[user_id])


def schedule_reminders(scheduler: AsyncIOScheduler, bot: Bot):
    reminders = load_reminders()
    for user_id, user_config in reminders.items():
        if user_config.reminder_time:
            hour, minute = map(int, user_config.reminder_time.split(":"))

            scheduler.add_job(
                send_reminder,
                trigger='cron',
                hour=hour,
                minute=minute,
                args=[bot, int(user_id)],
                id=f"reminder_{user_id}",
                replace_existing=True,
            )
        else:
            print(f"No reminder time for {user_id}")


async def send_reminder(bot: Bot, user_id: int):
    await bot.send_message(
        chat_id=user_id,
        text="📝 Time to record your daily diary entry! Send me a voice note when you're ready."
    )
