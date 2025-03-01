import telebot
import requests
import json

# 🔹 Bot Token & Owner ID
BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
OWNER_ID = "123456789"  # 🔹 अपनी Telegram User ID डालो

bot = telebot.TeleBot(BOT_TOKEN)

# 🔹 /ffstatus - Free Fire Server Status
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

# 🔹 बॉट को रन करो
if __name__ == '__main__':
    bot.polling(none_stop=True)
