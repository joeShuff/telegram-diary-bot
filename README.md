# 📝 Telegram Voice Diary Bot

A Telegram bot that helps you keep a voice-based daily diary — transcribed, styled, and sent back to you.

## 📦 Features

- ⏰ Daily reminders to submit your diary entry
- 🎤 Send a voice note — it'll be transcribed automatically
- ✍️ Bot formats your entry in your personal writing style
- 🧠 Powered by OpenAI's ChatGPT for stylistic transformation
- 💾 All voice notes and transcriptions are saved per user
- 🔧 User-configurable reminder times and diary style

![Voice Diary Example](art/example.gif)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/telegram-voice-diary-bot.git
cd telegram-voice-diary-bot
```

### 2. Set up environment variables

Create a `.env` file or export these in your environment:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

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

## 📁 Project Structure

```
project-root/
├── config/
│   ├── config.json                  # Reminder times per user (JSON format)
│   ├── audio/<user-id>/            # Voice notes organized by user ID
│   └── transcriptions/<user-id>/   # Transcribed text files organized by user ID
├── styles/  
│   ├── user_<user-id>_style.txt    # Stores a users style in text
```

## 💬 Bot Commands

- `/setstyle <text>` – Set your diary writing style using a sample entry
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

## License 📄

This project is licensed under the AGPL-3.0 License – see the [LICENSE](LICENSE) file for details.
