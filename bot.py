import os
import telebot
import requests
import json
from flask import Flask

# ✅ Telegram Bot Token
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"  # ✅ अपना टोकन यहां डालें

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Please check your code.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running successfully on Render!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 *Welcome!* 🌟\n\n"
                                      "/ffstatus - Free Fire server status\n"
                                      "/ffevents [region] - Free Fire events", 
                                      parse_mode='Markdown')

@bot.message_handler(commands=['ffstatus'])
def ffstatus(message):
    try:
        response = requests.get('https://ffstatusapi.vercel.app/api/freefire/normal/overview')
        bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['ffevents'])
def ffevents(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            return bot.reply_to(message, "ℹ️ Provide region code (e.g., IND)")
        
        response = requests.get(f'https://ff-event-nine.vercel.app/events?region={parts[1]}')
        bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ✅ Bot Polling (अलग थ्रेड में चलेगा)
def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    from threading import Thread
    Thread(target=run_bot).start()
    
    # ✅ Flask को 0.0.0.0 और पोर्ट 10000 पर रन करो
    app.run(host='0.0.0.0', port=10000)
