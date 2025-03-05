import telebot
import requests
import time
from io import BytesIO
import urllib.parse

BOT_TOKEN = "7090605258:AAGhLlwgEHw4KSogSqcV7Srho5I7GexLV6M"
bot = telebot.TeleBot(BOT_TOKEN)

# 📌 /start Command
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, 
        "🎮 *Welcome to Free Fire Bot!* 🔥\n\n"
        "📌 *Available Commands:*\n"
        "🎭 /ffevents [region] - Get Free Fire Events\n\n"
        "🔹 Example: /ffevents IND", parse_mode='Markdown')

# 📌 /ffevents Command
@bot.message_handler(commands=['ffevents'])
def handle_ffevents(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.reply_to(message, "ℹ️ *Please provide a region code!*\nExample: /ffevents IND", parse_mode='Markdown')
            return
        
        region = parts[1].upper().strip()  
        encoded_region = urllib.parse.quote(region)  

        # ✅ 1. लोडिंग मैसेज भेजें और तुरंत अपडेट करें
        loading_msg = bot.reply_to(message, "⏳ Loading... 0%")
        
        for i in range(10, 101, 10):
            bot.edit_message_text(f"⏳ Loading... {i}%", message.chat.id, loading_msg.message_id)
            time.sleep(0.1)  # बहुत ज़्यादा देरी नहीं होगी
        
        # ✅ 2. जैसे ही 100% पहुंचे, तुरंत API से डेटा लाएं
        url = f'https://ff-event-nine.vercel.app/events?region={encoded_region}'
        response = requests.get(url)

        # ✅ 3. 100% दिखाने के तुरंत बाद लोडिंग मैसेज हटा दें
        bot.delete_message(message.chat.id, loading_msg.message_id)

        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])

            if not events:
                bot.send_message(message.chat.id, f"❌ *No upcoming events found for {region}*", parse_mode='Markdown')
                return

            # ✅ 4. इवेंट्स को तुरंत भेजना शुरू करें
            for event in events:
                msg = f"🎭 *{event['poster-title']}*\n"
                msg += f"🕒 {event['start']} - {event['end']}\n"
                msg += f"📌 *Status:* {event['status']}\n"

                if event["desc"]:
                    msg += f"📖 *Details:* {event['desc'][:300]}...\n\n"

                # ✅ 5. इमेज भेजें (अगर उपलब्ध हो)
                if event["src"]:
                    img_response = requests.get(event["src"])
                    if img_response.status_code == 200:
                        img = BytesIO(img_response.content)
                        img.name = "event.jpg"
                        bot.send_photo(message.chat.id, img, caption=msg, parse_mode='Markdown')
                    else:
                        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
                else:
                    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

        else:
            bot.send_message(message.chat.id, f"🔴 *Error fetching events:* {response.status_code}", parse_mode='Markdown')

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ *Error:* {str(e)}", parse_mode='Markdown')

bot.polling(none_stop=True)
