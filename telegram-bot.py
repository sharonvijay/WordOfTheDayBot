import requests
import random
import os
import pytz
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WORDNIK_API_KEY = os.getenv("WORDNIK_API_KEY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Timezone for scheduling
IST = pytz.timezone("Asia/Kolkata")

# Static fallback words
STATIC_WORDS = [
    {"word": "Serendipity", "definition": "The occurrence of events by chance in a happy way.",
     "example": "It was pure serendipity that we found that charming little café."},
    {"word": "Ephemeral", "definition": "Lasting for a very short time.",
     "example": "The beauty of a sunset is ephemeral, lasting only a few minutes."},
    {"word": "Mellifluous", "definition": "Pleasant to hear.",
     "example": "Her mellifluous voice made the song even more beautiful."},
]

async def get_word_of_the_day():
    """Fetch word, definition, and example sentence from Wordnik API or static list."""
    if not WORDNIK_API_KEY:
        print("⚠️ WORDNIK_API_KEY not set, using static words.")
        return get_static_word()

    word_url = f"https://api.wordnik.com/v4/words.json/wordOfTheDay?api_key={WORDNIK_API_KEY}"
    
    try:
        response = requests.get(word_url)
        response.raise_for_status()
        data = response.json()

        word = data.get("word", "Unknown")
        definition = data["definitions"][0]["text"] if data.get("definitions") else "No definition found."
        example = data["examples"][0]["text"] if data.get("examples") else "No example available."

        return f"📖 *Word of the Day:* {word}\n📝 *Meaning:* {definition}\n✍️ *Example:* {example}"
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API request failed: {e}. Using static word.")
        return get_static_word()


def get_static_word():
    """Returns a random word, definition, and example sentence from the predefined list."""
    word_info = random.choice(STATIC_WORDS)
    return f"📖 *Word of the Day:* {word_info['word']}\n📝 *Meaning:* {word_info['definition']}\n✍️ *Example:* {word_info['example']}"

async def send_scheduled_word(application):
    """Sends the Word of the Day message at 8:00 AM IST."""
    message = await get_word_of_the_day()
    await application.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

def schedule_daily_word(application):
    """Schedules the Word of the Day message at 8:00 AM IST."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_scheduled_word, 'cron', hour=8, minute=0, timezone=IST, args=[application])
    scheduler.start()
    print("✅ Daily Word of the Day scheduled at 8:00 AM IST.")

async def word(update: Update, context: CallbackContext) -> None:
    """Handles the /word command."""
    message = await get_word_of_the_day()
    await update.message.reply_text(message, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("word", word))

    # Schedule the daily message
    schedule_daily_word(app)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
