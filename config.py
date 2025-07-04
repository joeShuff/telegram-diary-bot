import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

"""
Supported values are from langchain model. Built with support for 
google_genai
openai
"""
AI_PROVIDER = os.getenv("AI_PROVIDER")
AI_MODEL = os.getenv("AI_MODEL")