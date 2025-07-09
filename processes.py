import os

from telegram import Message

from const import TRANSCRIPTION_DIR
from diary_writer import generate_diary_entry
from paths import get_transcription_filename
from transcribe import transcribe_voice


async def audio_file_to_diary(telegram_message: Message, filepath: str) -> str:
    await telegram_message.reply_text("Transcribing...")
    text = transcribe_voice(filepath)

    user_id = telegram_message.chat.id

    transcription_filename = get_transcription_filename()
    transcription_path = os.path.join(TRANSCRIPTION_DIR, str(user_id), transcription_filename)

    os.makedirs(os.path.dirname(transcription_path), exist_ok=True)

    # Save transcription to file
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Send the transcription text file
    await telegram_message.reply_document(document=open(transcription_path, "rb"),
                                                  filename=transcription_filename,
                                                  caption="📝 Here's your transcription")

    await transcribed_file_to_diary(telegram_message, transcription_path)


async def transcribed_file_to_diary(telegram_message: Message, transcription_path: str) -> str:
    with open(transcription_path, "r", encoding="utf-8") as f:
        transcribed_text = f.read()

    await telegram_message.reply_text("Converting to diary entry...")
    user_id = telegram_message.chat.id
    diary = generate_diary_entry(transcribed_text, user_id)

    await telegram_message.reply_text(f"📔 Your entry:")
    await telegram_message.reply_text(diary)
