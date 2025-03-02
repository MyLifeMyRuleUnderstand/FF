import os
import json
import telebot
import requests
from flask import Flask, request, jsonify

# ✅ Telegram Bot Token
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"  
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Please check your code.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ✅ टोकन लोड करने का फंक्शन (हर सर्वर के लिए अलग JSON फाइल)
def load_tokens(server_name):
    try:
        if server_name == "IND":
            with open("token_ind.json", "r") as f:
                tokens = json.load(f)
        elif server_name in {"BR", "US", "SAC", "NA"}:
            with open("token_br.json", "r") as f:
                tokens = json.load(f)
        else:
            with open("token_bd.json", "r") as f:
                tokens = json.load(f)
        return tokens
    except Exception as e:
        app.logger.error(f"Error loading tokens for server {server_name}: {e}")
        return None

@app.route('/')
def home():
    return "✅ Bot is running successfully on Render!"

# ✅ स्टार्ट कमांड (बॉट के ऑप्शंस दिखाने के लिए)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 *Welcome!* 🌟\n\n"
                                      "/ffstatus - Free Fire server status\n"
                                      "/ffevents [region] - Free Fire events\n"
                                      "/likecheck [UID] [SERVER_NAME] - Check player likes", 
                                      parse_mode='Markdown')

# ✅ Free Fire Server Status चेक करने का फंक्शन
@bot.message_handler(commands=['ffstatus'])
def ffstatus(message):
    try:
        response = requests.get('https://ffstatusapi.vercel.app/api/freefire/normal/overview')
        bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ✅ Free Fire Events चेक करने का फंक्शन
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

# ✅ `/likecheck` कमांड - प्लेयर के लाइक्स चेक करने के लिए
@bot.message_handler(commands=['likecheck'])
def like_check(message):
    try:
        parts = message.text.split(' ')
        if len(parts) < 3:
            return bot.reply_to(message, "ℹ️ Usage: /likecheck [UID] [SERVER_NAME]")

        uid = parts[1]
        server_name = parts[2].upper()
        tokens = load_tokens(server_name)

        if not tokens:
            return bot.reply_to(message, "❌ Error loading tokens for server.")

        token = tokens[0]['token']
        # ✅ API कॉल (इसे अपनी API से रिप्लेस करें)
        response = requests.get(f"https://api.example.com/player_likes?uid={uid}&server={server_name}&token={token}")

        if response.status_code == 200:
            bot.send_message(message.chat.id, f"✅ Player Likes: {response.json().get('likes', 'Unknown')}")
        else:
            bot.send_message(message.chat.id, "❌ Failed to fetch player likes.")
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
