import telebot
import requests
import json
import urllib.parse
import os

BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
OWNER_ID = "21080390"  # Telegram User ID

bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUPS_FILE = 'allowed_groups.json'


# Allowed Groups को सेव करने का फ़ंक्शन
def save_allowed_groups(groups):
    with open(ALLOWED_GROUPS_FILE, 'w') as f:
        json.dump(groups, f)


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Welcome message handler"""
    start_text = (
        "🌟 *Welcome to the Bot!* 🌟\n\n"
        "Available commands:\n"
        "/ffstatus - Free Fire server status\n"
        "/ffevents [region] - Free Fire events"
    )
    bot.send_message(message.chat.id, start_text, parse_mode='Markdown')


@bot.message_handler(commands=['ffstatus'])
def handle_ffstatus(message):
    try:
        loading_msg = bot.reply_to(message, "⏳ Fetching Free Fire status...")
        response = requests.get('https://ffstatusapi.vercel.app/api/freefire/normal/overview')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching status: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")


@bot.message_handler(commands=['ffevents'])
def handle_ffevents(message):
    try:
        text_parts = message.text.split(' ', 1)
        if len(text_parts) < 2:
            bot.reply_to(message, "ℹ️ Please provide a region code after the command (e.g., IND)")
            return

        region = text_parts[1]
        loading_msg = bot.reply_to(message, "⏳ Fetching Free Fire events...")
        response = requests.get(f'https://ff-event-nine.vercel.app/events?region={region}')
        
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching events: {response.status_code}")
        
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")


if __name__ == '__main__':
    if not os.path.exists(ALLOWED_GROUPS_FILE):
        save_allowed_groups([])

    bot.polling(none_stop=True)
