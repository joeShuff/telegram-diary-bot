import os

import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

STYLE_DIR = os.getcwd() + "/config/styles"


def generate_diary_entry(raw_text: str, user_id: int) -> str:
    user_style = get_user_style(user_id)

    system_prompt = (
        f"You are a reflective diary-writing assistant. Instructions from the user about how to write a diary entry in their style is:\n\n"
        f"{user_style}\n\n"
        f"Convert the following transcription into a diary entry that matches the tone and language and rules set out by the user."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ]
    )
    return response.choices[0].message.content.strip()


def set_user_style(user_id: int, style: str):
    os.makedirs(STYLE_DIR, exist_ok=True)
    path = os.path.join(STYLE_DIR, f"user_{user_id}_style.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(style)


def get_user_style(user_id: int) -> str:
    path = os.path.join(STYLE_DIR, f"user_{user_id}_style.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "The user has not set a style. Use a thoughtful and personal tone."
