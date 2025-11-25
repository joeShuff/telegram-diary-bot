# 📝 Telegram Voice Diary Bot

A Telegram bot that helps you keep a voice-based daily diary — transcribed, styled, and sent back to you.

## 📦 Features

- ⏰ Daily reminders to submit your diary entry
- 🎤 Send a voice note — it'll be transcribed automatically
- ✍️ Bot formats your entry in your personal writing style
- 🧠 Powered by whatever AI provider you want for stylistic transformation
- 💾 All voice notes and transcriptions are saved per user
- 🔧 User-configurable reminder times and diary style
- 🔧 Plugin system for integrating with third party providers.

![Voice Diary Example](art/example.gif)

## Docker Get Started

### 1. Compose
Download the `docker-compose.yml` file or copy the contents from the raw file [here](https://raw.githubusercontent.com/joeShuff/telegram-diary-bot/main/docker-compose.yml)

### 2. Populate environment variables
Consult the **Environment Variables** table to see what variables are and aren't needed.

### 3. Run
Run the container and test your bot!

## Local Get Started

### 1. Clone the repository

```bash
git clone https://github.com/joeShuff/telegram-diary-bot.git
cd telegram-diary-bot
```

### 2. Set up environment variables

See Environment Variables section below

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the bot

```bash
python bot.py
```

Or build and run with Docker:

```bash
docker build -t diary-bot .
docker run --env-file .env diary-bot
```

## Environment Variables
See table for an explanation of what environment variables are needed/supported and their use.

| Variable Name     | Description                                                                                                                                | Required                             | Example Value                |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|------------------------------|
| `TELEGRAM_TOKEN`  | The token for your Telegram bot. Get it from [@BotFather](https://t.me/BotFather)                                                          | ✅ Yes                                | `123456:ABC-DEF1234ghIkl...` |
| `AI_PROVIDER`     | Which AI model to use: `openai` or `google_genai`. See [langchain](https://python.langchain.com/docs/integrations/providers/) for details. | ✅ Yes                                | `openai`                     |
| `AI_MODEL`        | The AI model you want to use. See your selected provider for names.                                                                        | ✅ Yes                                | `gpt-4.1-nano`               |
| `OPENAI_API_KEY`  | Your OpenAI API key for diary stylization (used with GPT)                                                                                  | ⚠️ Yes (if using OpenAI)             | `sk-xxxxxxxxxxxxxxxxxxxxxx`  |
| `GOOGLE_API_KEY`  | Your Google API key if using Gemini (via LangChain)                                                                                        | ⚠️ Yes (if using Gemini)             | `AIzaSyD-xxxxxxxxxxxxxxxxx`  |
| `AI_TEMPERATURE`  | Controls creativity of diary output (0.0 = predictable, 1.0 = creative)                                                                    | ❌ Optional (default: 0.7)            | `0.7`                        |
| `ENABLED_PLUGINS` | List of plugin IDs to enable for this bot host.                                                                                            | ❌ Optional (default: diary_feedback) | `diary_feedback`             |

## 📁 Project Structure

```
project-root/
├── config/
│   ├── config.json                  # Reminder times per user (JSON format)
│   ├── audio/<user-id>/            # Voice notes organized by user ID
│   └── transcriptions/<user-id>/   # Transcribed text files organized by user ID
├── styles/  
│   ├── user_<user-id>_style.txt    # Stores a users style in text
├── plugins/
│   ├── *Any plugin files*
```

## 💬 Bot Commands

- `/setstyle <text>` – Set your diary writing style using a sample entry
- `/getstyle` - Returns a users style to confirm your style
- `/setreminder <HH:MM>` – Set your daily reminder time (bot's local time)
- `/start` – Starter command

## 🛠 Configuration

User reminder times are stored in `config/config.json`:

```json
{
  "123456789": "08:30",
  "987654321": "21:00"
}
```

## 🛠 Plugins
Currently, the bot comes built with 2 plugins

### Diary Feedback
Plugin ID: `diary_feedback`

This plugin simply sends the diary entry to the chat as a response.

### Journiv
Plugin ID: `journiv`

[Journiv](https://journiv.com/) is a self-hosted diary system. This plugin can send your entries to a specified Journiv Journal and also attach the voice note.

Run `/journivsetup` to setup your connection to Journiv (user specific)

## Developing more plugins
Right now the documentation is the existing plugins. This area might get more info in the future.

## License 📄

This project is licensed under the AGPL-3.0 License – see the [LICENSE](LICENSE) file for details.
