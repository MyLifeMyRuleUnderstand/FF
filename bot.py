import os
import json
import requests
import asyncio
import telebot
from flask import Flask, request, jsonify
from google.protobuf.json_format import MessageToJson

# ✅ Telegram Bot Token
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Please check your code.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ✅ Load Tokens Function
def load_tokens(server_name):
    file_map = {
        "IND": "token_ind.json",
        "BR": "token_br.json",
        "US": "token_br.json",
        "SAC": "token_br.json",
        "NA": "token_br.json"
    }
    file_name = file_map.get(server_name, "token_bd.json")

    if not os.path.exists(file_name):
        return {"error": f"❌ Token file '{file_name}' not found"}

    try:
        with open(file_name, "r") as f:
            tokens = json.load(f)
        return tokens
    except json.JSONDecodeError:
        return {"error": f"❌ Invalid JSON format in '{file_name}'"}
    except Exception as e:
        return {"error": f"❌ Error loading tokens: {str(e)}"}

# ✅ API Endpoint for Likes
@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    if not uid or not server_name:
        return jsonify({"error": "❌ UID and server_name are required"}), 400

    try:
        tokens = load_tokens(server_name)
        if "error" in tokens:
            return jsonify(tokens), 400
        token = tokens[0]['token']
        
        # यहाँ पर आपकी लाइक प्रोसेसिंग लॉजिक रहेगी
        result = {
            "message": "✅ Like process initiated!",
            "UID": uid,
            "Server": server_name
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Telegram Bot Commands
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🌟 *Welcome!* 🌟\n\n"
                                      "/ffstatus - Free Fire server status\n"
                                      "/ffevents region - Free Fire events\n"
                                      "/likecheck UID SERVER - Check likes", 
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

# ✅ `/likecheck` Command for Checking Likes
@bot.message_handler(commands=['likecheck'])
def likecheck(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            return bot.reply_to(message, "❌ Usage: /likecheck UID SERVER_NAME")
        
        uid, server_name = parts[1], parts[2].upper()
        tokens = load_tokens(server_name)
        if "error" in tokens:
            return bot.send_message(message.chat.id, tokens["error"])

        bot.send_message(message.chat.id, f"✅ Checking likes for UID: {uid} on server {server_name}...")
        # यहाँ पर लाइक्स चेक करने की API कॉल हो सकती है

        fake_likes = 120  # (Demo के लिए)
        bot.send_message(message.chat.id, f"📊 UID {uid} has {fake_likes} likes on {server_name}.")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

# ✅ Run Bot & Flask Together
def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    from threading import Thread
    Thread(target=run_bot).start()
    
    # ✅ Flask को 0.0.0.0 और पोर्ट 10000 पर रन करो
    app.run(host='0.0.0.0', port=10000)
