from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from plugin_core import BasePlugin


@dataclass
class JournivConfig:
    base_url: str
    access_token: str
    refresh_token: str
    journal_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to a JSON-serializable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a dataclass instance from stored dict."""
        return cls(**data)


class JournivPlugin(BasePlugin):
    """
    Plugin functions
    """

    def load_config(self, user_id: int) -> JournivConfig:
        dict = super().load_config(user_id)
        return JournivConfig.from_dict(dict)

    def load(self, application: Application):
        """Registers commands and handlers."""
        application.add_handler(CommandHandler("journivsetup", self.setup_command))
        application.add_handler(CallbackQueryHandler(self.select_journal,
                                                     pattern="^journiv_select_"))

    def get_id(self):
        return "journiv"

    def on_entry(self, entry_text, transcription_file, voice_note_file, telegram):
        telegram.send_message("Processing with Journiv plugin…")
        # JOURNIV API LOGIC HERE
        telegram.send_message("Entry saved to Journiv!")

    """
    Setup Functions
    """

    async def setup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Usage: /journivsetup <base_url> <email> <password>"
            )
            return

        base_url = args[0]
        email = args[1]
        password = args[2]

        # Validate API
        try:
            credentials = await self.journiv_login(base_url, email, password)
        except Exception as e:
            return await update.message.reply_text(str(e))

        config = JournivConfig(
            base_url=base_url,
            access_token=credentials["access_token"],
            refresh_token=credentials["refresh_token"],
            journal_id=""
        )

        self.save_config(
            update.effective_user.id,
            config.to_dict()
        )

        try:
            journals = await self.load_journals(update.effective_user.id)
        except Exception as e:
            return await update.message.reply_text(str(e))

        if len(journals) == 1:
            config.journal_id = journals[0]["id"]

            self.save_config(
                update.effective_user.id,
                config.to_dict()
            )

            return await update.message.reply_text(
                f"Setup complete. Logging to: {journals[0]['title']}"
            )

        keyboard = [
            [
                InlineKeyboardButton(
                    j["title"],
                    callback_data=f"journiv_select_{j['id']}_{j['title']}"
                )
            ] for j in journals
        ]

        await update.message.reply_text(
            "Setup complete. Choose which journal entries should be uploaded to:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def select_journal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        journal_id, journal_name = query.data[len("journiv_select_"):].split("_")

        stored_data = self.load_config(update.effective_user.id)

        new_config = JournivConfig(
            base_url=stored_data.base_url,
            access_token=stored_data.access_token,
            refresh_token=stored_data.refresh_token,
            journal_id=journal_id
        )

        self.save_config(
            update.effective_user.id,
            new_config.to_dict()
        )

        await query.edit_message_text(f"Journiv setup complete for journal {journal_name}!")

    """
    Helper Functions
    """

    async def load_journals(self, user_id: int) -> List[Dict]:
        """
        Fetch the list of journals for the current user from Journiv.

        Args:
            user_id (str): ID of the user to load journals for

        Returns:
            List[Dict]: List of journal objects, e.g. [{"id": "123", "name": "Work"}, ...]

        Raises:
            RuntimeError: If the request fails or returns unexpected data
        """
        config = self.load_config(user_id)
        base_url = config.base_url

        url = f"{base_url.rstrip('/')}/api/v1/journals/?include_archived=false"

        headers = {
            "Authorization": f"Bearer {config.access_token}",
            "Accept": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 401:
                        raise ValueError("Invalid or expired access token.")
                    if resp.status >= 400:
                        text = await resp.text()
                        raise RuntimeError(f"Failed to fetch journals: {resp.status}, {text}")

                    data = await resp.json()

            except aiohttp.ClientError as e:
                raise RuntimeError(f"Network error contacting Journiv: {e}")

        # Ensure data is a list
        if not isinstance(data, list):
            raise RuntimeError(f"Unexpected response from Journiv API: {data}")

        return data

    async def journiv_login(self, base_url: str, email: str, password: str):
        """
        Attempt to log into Journiv and return tokens.
        Raises ValueError on invalid credentials.
        Raises RuntimeError on unexpected server errors.
        """

        url = f"{base_url.rstrip('/')}/api/v1/auth/login"
        payload = {
            "email": email,
            "password": password
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as resp:
                    # If journiv returns 401 / 403 on invalid login:
                    if resp.status in (401, 403):
                        raise ValueError("Invalid email or password.")

                    if resp.status >= 500:
                        raise RuntimeError("Journiv server error.")

                    if resp.status != 200:
                        text = await resp.text()
                        raise RuntimeError(
                            f"Unexpected response from Journiv ({resp.status}): {text}"
                        )

                    data = await resp.json()

            except aiohttp.ClientError as e:
                raise RuntimeError(f"Network error contacting Journiv: {e}")

        # Validate JSON structure
        if "access_token" not in data or "refresh_token" not in data:
            raise RuntimeError("Journiv login succeeded but tokens are missing.")

        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"]
        }
