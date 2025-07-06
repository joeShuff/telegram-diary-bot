import os


def get_float_env(var_name, default):
    try:
        value = os.getenv(var_name)
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        print(f"There was an error parsing {var_name}")
        return default


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

"""
Supported values are from langchain model. Built with support for 
google_genai
openai
"""
AI_PROVIDER = os.getenv("AI_PROVIDER")
AI_MODEL = os.getenv("AI_MODEL")
AI_TEMPERATURE = get_float_env("AI_TEMPERATURE", 0.7)
