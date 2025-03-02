import os
import json
import requests
import asyncio
import binascii
import aiohttp
import telebot
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
from google.protobuf.message import DecodeError
import like_pb2
import like_count_pb2
import uid_generator_pb2

# Flask App
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN)

def load_tokens(server_name):
    try:
        file_map = {
            "IND": "token_ind.json",
            "BR": "token_br.json",
            "US": "token_br.json",
            "SAC": "token_br.json",
            "NA": "token_br.json"
        }
        file_name = file_map.get(server_name, "token_bd.json")
        with open(file_name, "r") as f:
            return json.load(f)
    except Exception as e:
        app.logger.error(f"Error loading tokens for server {server_name}: {e}")
        return None

def encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        return binascii.hexlify(cipher.encrypt(padded_message)).decode('utf-8')
    except Exception as e:
        app.logger.error(f"Error encrypting message: {e}")
        return None

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except DecodeError as e:
        app.logger.error(f"Error decoding Protobuf data: {e}")
        return None

def make_request(encrypt, server_name, token):
    url_map = {
        "IND": "https://client.ind.freefiremobile.com/GetPlayerPersonalShow",
        "BR": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "US": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "SAC": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "NA": "https://client.us.freefiremobile.com/GetPlayerPersonalShow"
    }
    url = url_map.get(server_name, "https://clientbp.ggblueshark.com/GetPlayerPersonalShow")
    
    try:
        headers = {
            'User-Agent': "Dalvik/2.1.0",
            'Connection': "Keep-Alive",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded"
        }
        response = requests.post(url, data=bytes.fromhex(encrypt), headers=headers, verify=False)
        return decode_protobuf(response.content) if response.ok else None
    except Exception as e:
        app.logger.error(f"Error in make_request: {e}")
        return None

# ✅ Telegram Bot Functionality
@bot.message_handler(commands=['likecheck'])
def handle_likecheck(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ Usage: `/likecheck <UID> <Region>`")
            return
        
        uid, server_name = parts[1], parts[2].upper()
        tokens = load_tokens(server_name)
        if not tokens:
            bot.reply_to(message, "❌ Token loading error.")
            return
        
        token = tokens[0]['token']
        encrypted_uid = encrypt_message(uid.encode())
        if not encrypted_uid:
            bot.reply_to(message, "❌ Encryption failed.")
            return

        before = make_request(encrypted_uid, server_name, token)
        if not before:
            bot.reply_to(message, "❌ Failed to fetch initial likes.")
            return
        
        data_before = json.loads(MessageToJson(before))
        before_likes = int(data_before.get('AccountInfo', {}).get('Likes', 0))
        player_name = data_before.get('AccountInfo', {}).get('PlayerNickname', '')

        bot.reply_to(message, f"✅ {player_name} ({uid}) has {before_likes} likes.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ✅ Flask Route for Telegram Bot Webhook (Optional)
@app.route('/webhook', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

# ✅ Flask Route for `/like` API
@app.route('/like', methods=['GET'])
def handle_requests():
    uid = request.args.get("uid")
    server_name = request.args.get("server_name", "").upper()
    if not uid or not server_name:
        return jsonify({"error": "UID and server_name are required"}), 400

    try:
        def process_request():
            tokens = load_tokens(server_name)
            if tokens is None:
                raise Exception("Failed to load tokens.")
            token = tokens[0]['token']
            encrypted_uid = encrypt_message(uid.encode())
            if encrypted_uid is None:
                raise Exception("Encryption of UID failed.")

            before = make_request(encrypted_uid, server_name, token)
            if before is None:
                raise Exception("Failed to retrieve initial player info.")
            try:
                jsone = MessageToJson(before)
            except Exception as e:
                raise Exception(f"Error converting 'before' protobuf to JSON: {e}")
            data_before = json.loads(jsone)
            before_like = int(data_before.get('AccountInfo', {}).get('Likes', 0))

            result = {
                "LikesBeforeCommand": before_like,
                "PlayerNickname": data_before.get('AccountInfo', {}).get('PlayerNickname', ''),
                "UID": int(data_before.get('AccountInfo', {}).get('UID', 0))
            }
            return result

        result = process_request()
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    bot.polling(none_stop=True)
    app.run(debug=True, use_reloader=False)
