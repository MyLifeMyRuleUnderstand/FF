import telebot
import requests
import json
import os

BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"  # ✅ सही फॉर्मेट

bot = telebot.TeleBot(BOT_TOKEN)

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

bot.polling()
