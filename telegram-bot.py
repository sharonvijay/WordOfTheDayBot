import requests
import random
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot


# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WORDNIK_API_KEY = os.getenv("WORDNIK_API_KEY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


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

async def send_word():
    """Fetches and sends the Word of the Day to Telegram."""
    if not TOKEN or not CHAT_ID:
        print("⚠️ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment variables.")
        return

    message = await get_word_of_the_day()
    bot = Bot(token=TOKEN)
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
        print("✅ Word of the Day sent successfully!")
    except Exception as e:
        print(f"⚠️ Failed to send message: {e}")

async def main():
    """Fetches the Word of the Day and sends it to Telegram, then exits."""
    await send_word()

if __name__ == "__main__":
    asyncio.run(main())