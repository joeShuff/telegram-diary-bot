from telegram import Message

from plugin_core import BasePlugin


class FeedbackPlugin(BasePlugin):

    def get_id(self) -> str:
        return "diary_feedback"

    def load(self, application):
        pass

    async def on_entry(self, source_message: Message, transcription_path, voice_note_path, diary_entry: str):
        await source_message.reply_text(f"📔 Your entry:")
        await source_message.reply_text(diary_entry)
