import os
import telebot
import requests
import json
import asyncio
from flask import Flask, request, jsonify

# ✅ Telegram Bot Token
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Please check your code.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running successfully on Render!"

# ✅ Like Check Command for Telegram Bot
@bot.message_handler(commands=['likecheck'])
def like_check(message):
    try:
        parts = message.text.split(' ')
        if len(parts) < 3:
            return bot.reply_to(message, "ℹ️ Usage: `/likecheck <UID> <SERVER_NAME>`", parse_mode="Markdown")
        
        uid = parts[1]
        server_name = parts[2].upper()
        result = check_likes(uid, server_name)

        if "error" in result:
            bot.send_message(message.chat.id, f"❌ Error: {result['error']}")
        else:
            bot.send_message(message.chat.id, f"📊 *Player:* `{result['PlayerNickname']}`\n"
                                              f"🆔 *UID:* `{result['UID']}`\n"
                                              f"❤️ *Likes:* `{result['Likes']}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ✅ Check Likes Function
def check_likes(uid, server_name):
    tokens = load_tokens(server_name)
    if tokens is None:
        return {"error": "Failed to load tokens."}
    
    token = tokens[0]['token']
    encrypted_uid = enc(uid)
    if encrypted_uid is None:
        return {"error": "Encryption of UID failed."}

    player_info = make_request(encrypted_uid, server_name, token)
    if player_info is None:
        return {"error": "Failed to retrieve player info."}

    try:
        jsone = MessageToJson(player_info)
        data = json.loads(jsone)
    except Exception as e:
        return {"error": f"Error converting protobuf to JSON: {e}"}

    likes = int(data.get('AccountInfo', {}).get('Likes', 0))
    player_uid = int(data.get('AccountInfo', {}).get('UID', 0))
    player_name = str(data.get('AccountInfo', {}).get('PlayerNickname', ''))

    return {
        "Likes": likes,
        "PlayerNickname": player_name,
        "UID": player_uid
    }

# ✅ Telegram Bot Commands
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 *Welcome!* 🌟\n\n"
                                      "/ffstatus - Free Fire server status\n"
                                      "/ffevents [region] - Free Fire events\n"
                                      "/likecheck <UID> <SERVER_NAME> - Check player likes", 
                                      parse_mode='Markdown')

# ✅ Run bot in background
def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
