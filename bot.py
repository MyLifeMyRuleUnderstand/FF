import telebot
import requests
import json

# Telegram Bot Token
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"

# बॉट को इनिशियलाइज़ करना
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    """बॉट का वेलकम मैसेज"""
    start_text = "🌟 *Welcome to the Bot!* 🌟\n\n" \
                 "Available commands:\n" \
                 "/ffstatus - Free Fire server status"
    bot.send_message(message.chat.id, start_text, parse_mode='Markdown')

@bot.message_handler(commands=['ffstatus'])
def handle_ffstatus(message):
    """Free Fire का स्टेटस चेक करने वाला फंक्शन"""
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

if __name__ == '__main__':
    bot.polling(none_stop=True)
