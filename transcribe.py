import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def transcribe_voice(filepath: str) -> str:
    with open(filepath, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]
