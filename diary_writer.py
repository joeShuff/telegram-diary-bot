import os
from langchain.chat_models import init_chat_model

import config

STYLE_DIR = os.getcwd() + "/config/styles"


def generate_diary_entry(raw_text: str, user_id: int) -> str:
    user_style = get_user_style(user_id)

    prompt = (
        f"You are a reflective diary-writing assistant. Instructions from the user about how to write a diary entry in their style is:\n\n"
        f"{user_style}\n\n"
        f"Convert the following transcription into a diary entry that matches the tone and language and rules set out by the user. RESPOND ONLY WITH THE STYLED DIARY ENTRY.\n\n"
        f"{raw_text}"
    )

    model = init_chat_model(model=config.AI_MODEL, model_provider=config.AI_PROVIDER)

    response = model.invoke(prompt)
    return response.content


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
