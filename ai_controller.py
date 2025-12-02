from telegram import Update
from telegram.ext import ContextTypes

import user_config


def set_enable_ai_processing(user_id: int, enabled: bool):
    stored_config = user_config.load_user_config(user_id)

    stored_config.ai_enabled = enabled

    user_config.save_user_config(user_id, stored_config)


async def enable_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_enable_ai_processing(update.effective_user.id, True)
    await update.message.reply_text("🤖 Enabled AI processing")


async def disable_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_enable_ai_processing(update.effective_user.id, False)
    await update.message.reply_text("🤖 Disabled AI processing")
