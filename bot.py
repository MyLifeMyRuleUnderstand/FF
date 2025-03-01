import telebot
import requests
import json
import urllib.parse
import os

BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
OWNER_ID = "21080390"  # Telegram User ID नहीं, API_ID है

bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_GROUPS_FILE = 'allowed_groups.json'

def load_allowed_groups():
    """Load allowed groups from JSON file"""
    if not os.path.exists(ALLOWED_GROUPS_FILE):
        return []
    with open(ALLOWED_GROUPS_FILE, 'r') as f:
        return json.load(f).get('allowed_groups', [])

def save_allowed_groups(groups):
    """Save allowed groups to JSON file"""
    with open(ALLOWED_GROUPS_FILE, 'w') as f:
        json.dump({'allowed_groups': groups}, f)

def group_allowed(message):
    """Check if group is allowed"""
    if message.chat.type in ['group', 'supergroup']:
        return str(message.chat.id) in load_allowed_groups()
    return True

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
@group_check
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
@group_check
def handle_ffevents(message):
    try:
        region = message.text.split(' ', 1)[1]
        loading_msg = bot.reply_to(message, "⏳ Fetching Free Fire events...")
        response = requests.get(f'https://ff-event-nine.vercel.app/events?region={region}')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching events: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except IndexError:
        bot.reply_to(message, "ℹ️ Please provide a region code after the command (e.g., IND)")
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")







if __name__ == '__main__':
    if not os.path.exists(ALLOWED_GROUPS_FILE):
        save_allowed_groups([])
    bot.polling(none_stop=True)
    
#Made By PRINCE-MODZ
