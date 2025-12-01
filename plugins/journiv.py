from dataclasses import dataclass, asdict, fields
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from plugin_core import BasePlugin
from plugins.journiv_api import load_journals, journiv_login, upload_journiv_entry, journiv_refresh, upload_media


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

    def is_valid(self) -> bool:
        for f in fields(self):
            value = getattr(self, f.name)
            if not isinstance(value, str) or not value.strip():
                return False
        return True


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

    async def on_entry(self, source_message: Message, transcription_path, voice_note_path, diary_entry: str):
        stored_data = self.load_config(source_message.chat.id)

        if not stored_data.is_valid():
            print(f"Skipping journiv for {source_message.chat.id} because no valid config")
            return

        await source_message.reply_text("Processing with Journiv plugin…")

        try:
            await self.refresh_token(source_message.chat.id)
            stored_data = self.load_config(source_message.chat.id)

            uploaded_entry = await upload_journiv_entry(
                base_url=stored_data.base_url,
                access_token=stored_data.access_token,
                journal_id=stored_data.journal_id,
                content=diary_entry
            )

            entry_id = uploaded_entry["id"]
            journal_id = uploaded_entry["journal_id"]

            await upload_media(
                base_url=stored_data.base_url,
                access_token=stored_data.access_token,
                file_path=voice_note_path,
                entry_id=entry_id
            )

            entry_url = f"{stored_data.base_url}/#/entries/{entry_id}/edit?journalId={journal_id}"
            keyboard = [
                [InlineKeyboardButton("Open Entry ↗️", url=entry_url)]
            ]
            markup = InlineKeyboardMarkup(keyboard)

            await source_message.reply_text(
                text="✨ *Entry created!* Tap below to view or edit it:",
                reply_markup=markup,
                parse_mode="Markdown",
            )

        except Exception as e:
            await source_message.reply_text(f"Upload failed:\n{e}")

    async def refresh_token(self, user_id):
        """
        This function loads the users config, performs the token refresh then stores the new tokens in the config
        :param user_id: User ID to perform the refresh for
        """
        stored_config = self.load_config(user_id)

        new_data = await journiv_refresh(
            base_url=stored_config.base_url,
            refresh_token=stored_config.refresh_token
        )

        new_config = JournivConfig(
            base_url=stored_config.base_url,
            access_token=new_data["access_token"],
            refresh_token=stored_config.refresh_token,  # No new refresh token issued
            journal_id=stored_config.journal_id
        )

        self.save_config(user_id, new_config.to_dict())

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
            credentials = await journiv_login(base_url, email, password)
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
            journals = await load_journals(config.base_url, config.access_token)
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
