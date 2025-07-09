import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ITEMS_PER_PAGE = 5


async def send_file_buttons(
        update_or_query,
        prompt: str,
        file_emoji: str,
        directory: str,
        callback_prefix: str,
        page: int = 1
):
    if not os.path.exists(directory):
        await update_or_query.message.reply_text("❌ No files found.")
        return

    files = [f for f in os.listdir(directory)]

    def extract_timestamp(filename):
        try:
            return int(filename.rsplit("_", 1)[-1].split(".")[0])
        except:
            return 0

    files.sort(key=extract_timestamp, reverse=True)

    total_pages = (len(files) - 1) // ITEMS_PER_PAGE + 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_files = files[start:end]

    buttons = [[
        InlineKeyboardButton(f"{file_emoji} {f}", callback_data=f"{callback_prefix}_process|{f}")
    ] for f in page_files]

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{callback_prefix}_page|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"{callback_prefix}_page|{page + 1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    markup = InlineKeyboardMarkup(buttons)

    if hasattr(update_or_query, "edit_message_text"):
        await update_or_query.edit_message_text(prompt, reply_markup=markup)
    else:
        await update_or_query.message.reply_text(prompt, reply_markup=markup)
