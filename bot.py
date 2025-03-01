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
        "/ytinfo [url] - YouTube video info\n"
        "/repoinfo [user] [repo] - GitHub repo info\n"
        "/ffinfo [player_id] - Free Fire player info\n"
        "/ffevents [region] - Free Fire events\n"
        "/mapinfo [region] [map_code] - Map information\n"
        "\nAdmin commands (Owner only):\n"
        "/allowgroup - Allow current group\n"
        "/disallowgroup - Disallow current group"
    )
    bot.send_message(message.chat.id, start_text, parse_mode='Markdown')

@bot.message_handler(commands=['allowgroup'])
def handle_allowgroup(message):
    """Allow current group (Owner only)"""
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "ℹ️ This command can only be used in groups.")
        return
    
    groups = load_allowed_groups()
    group_id = str(message.chat.id)
    
    if group_id not in groups:
        groups.append(group_id)
        save_allowed_groups(groups)
        bot.reply_to(message, f"✅ Group *{message.chat.title}* (`{group_id}`) has been allowed.", parse_mode='Markdown')
    else:
        bot.reply_to(message, "ℹ️ This group is already allowed.")

@bot.message_handler(commands=['disallowgroup'])
def handle_disallowgroup(message):
    """Disallow current group (Owner only)"""
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "ℹ️ This command can only be used in groups.")
        return
    
    groups = load_allowed_groups()
    group_id = str(message.chat.id)
    
    if group_id in groups:
        groups.remove(group_id)
        save_allowed_groups(groups)
        bot.reply_to(message, f"❌ Group *{message.chat.title}* (`{group_id}`) has been disallowed.", parse_mode='Markdown')
    else:
        bot.reply_to(message, "ℹ️ This group wasn't allowed.")

def group_check(func):
    """Decorator to check group permissions"""
    def wrapper(message):
        if not group_allowed(message):
            bot.reply_to(message, "🚫 Group not allowed")
            return
        return func(message)
    return wrapper


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

@bot.message_handler(commands=['ytinfo'])
@group_check
def handle_ytinfo(message):
    try:
        url = message.text.split(' ', 1)[1]
        loading_msg = bot.reply_to(message, "⏳ Fetching YouTube info...")
        response = requests.get(f'https://lkteam-yt-info-api-v1.vercel.app/video_info?url={urllib.parse.quote(url)}')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching YouTube info: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except IndexError:
        bot.reply_to(message, "ℹ️ Please provide a YouTube URL after the command")
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")

@bot.message_handler(commands=['repoinfo'])
@group_check
def handle_repoinfo(message):
    try:
        _, username, reponame = message.text.split()
        loading_msg = bot.reply_to(message, "⏳ Fetching GitHub repo info...")
        response = requests.get(f'https://githubrepoinfo-lkteam.vercel.app/repo?user={username}&repo={reponame}')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching repo info: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except ValueError:
        bot.reply_to(message, "ℹ️ Please provide username and reponame after the command")
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")

@bot.message_handler(commands=['ffinfo'])
@group_check
def handle_ffinfo(message):
    try:
        player_id = message.text.split(' ', 1)[1]
        loading_msg = bot.reply_to(message, "⏳ Fetching Free Fire account info...")
        response = requests.get(f'https://lk-team-ffinfo-five.vercel.app/ffinfo?id={player_id}')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching account info: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except IndexError:
        bot.reply_to(message, "ℹ️ Please provide a player ID after the command")
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

@bot.message_handler(commands=['mapinfo'])
@group_check
def handle_mapinfo(message):
    try:
        _, region, map_code = message.text.split()
        loading_msg = bot.reply_to(message, "⏳ Fetching map info...")
        encoded_map_code = urllib.parse.quote(map_code, safe="")
        response = requests.get(f'https://ffmapinfo-lk-team.vercel.app/get_map_info?region={region}&map_code={encoded_map_code}')
        if response.status_code == 200:
            bot.send_message(message.chat.id, f'```json\n{json.dumps(response.json(), indent=2)}\n```', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, f"❌ Error fetching map info: {response.status_code}")
        bot.delete_message(message.chat.id, loading_msg.message_id)
    except ValueError:
        bot.reply_to(message, "ℹ️ Please provide region and map_code after the command\nExample: /mapinfo BR #FREEFIRE...")
    except Exception as e:
        bot.send_message(message.chat.id, f"🚫 Error: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists(ALLOWED_GROUPS_FILE):
        save_allowed_groups([])
    bot.polling(none_stop=True)
    
#Made By PRINCE-MODZ