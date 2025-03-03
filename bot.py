import logging
import requests
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, ContextTypes

# OpenAI API और Telegram Bot Token लोड करें (Environment Variables से)
from dotenv import load_dotenv
import os

load_dotenv()  # .env फाइल को लोड करें

openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

if not openai_api_key or not telegram_bot_token:
    raise ValueError("⚠️ API Key या Bot Token सेट नहीं किया गया!")
  
# लॉगिंग सेटअप करें (फाइल में सेव करने के लिए)
logging.basicConfig(
    filename="bot_logs.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ Start Command (Welcome Message)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("💬 पूछें", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("🔍 OpenAI Website", url="https://openai.com/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = """
🔹 *Welcome to AI Telegram Bot!*  
यह बॉट OpenAI API का उपयोग करके आपके सवालों का जवाब दे सकता है और इमेज जेनरेट कर सकता है।  
नीचे दिए गए कमांड्स का उपयोग करें:  

- `/ask [सवाल]` - ChatGPT से जवाब पाएं।  
- `/image [विवरण]` - OpenAI से इमेज बनवाएं।  
- `/help` - सभी कमांड्स देखें।  
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# ✅ Ask Command (ChatGPT से जवाब)
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.replace("/ask", "").strip()
    if not user_input:
        await update.message.reply_text("⚠️ कृपया `/ask` के बाद अपना प्रश्न लिखें।", parse_mode='Markdown')
        return

    try:
        response = requests.post("https://api.openai.com/v1/completions",
                                 headers={"Authorization": f"Bearer {openai_api_key}"},
                                 json={"model": "text-davinci-003", "prompt": user_input, "max_tokens": 1024, "temperature": 0.5})
        response_json = response.json()
        response_text = response_json["choices"][0]["text"].strip() if "choices" in response_json else "❌ कोई उत्तर नहीं मिला।"

        sent_message = await update.message.reply_text(response_text, parse_mode='Markdown')

        # ✅ Auto-delete after 60 seconds
        await asyncio.sleep(60)
        await sent_message.delete()
        await update.message.delete()

    except Exception as e:
        logging.error(f"Error in ask_command: {e}")
        await update.message.reply_text("⚠️ कुछ समस्या हुई, कृपया बाद में प्रयास करें।")

# ✅ Image Command (OpenAI से इमेज जेनरेट करें)
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.replace("/image", "").strip()
    if not user_input:
        await update.message.reply_text("⚠️ कृपया `/image` के बाद इमेज विवरण लिखें।", parse_mode='Markdown')
        return

    try:
        response = requests.post("https://api.openai.com/v1/images/generations",
                                 headers={"Authorization": f"Bearer {openai_api_key}"},
                                 json={"prompt": user_input, "n": 1, "size": "1024x1024"})
        response_json = response.json()
        image_url = response_json["data"][0]["url"] if "data" in response_json else "❌ इमेज नहीं मिल सकी।"

        await update.message.reply_photo(photo=image_url, caption="🔹 आपकी इमेज तैयार है!")

    except Exception as e:
        logging.error(f"Error in image_command: {e}")
        await update.message.reply_text("⚠️ कुछ समस्या हुई, कृपया बाद में प्रयास करें।")

# ✅ Help Command (सभी कमांड्स दिखाएं)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
📌 *AI Bot Commands:*  
- `/start` - बॉट शुरू करें।  
- `/ask [सवाल]` - OpenAI से जवाब पाएं।  
- `/image [विवरण]` - AI से इमेज बनवाएं।  
- `/help` - कमांड्स की सूची देखें।  

🔹 *Created by:* AI Developer  
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ✅ Rate Limit (Anti-Spam) सिस्टम
user_last_request = {}

async def rate_limiter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.message.from_user.id
    current_time = update.message.date.timestamp()

    if user_id in user_last_request:
        last_time = user_last_request[user_id]
        if current_time - last_time < 5:  # 5 सेकंड का गैप जरूरी है
            await update.message.reply_text("⚠️ कृपया धीमे चलें, आप बहुत तेज़ी से रिक्वेस्ट भेज रहे हैं।")
            return False

    user_last_request[user_id] = current_time
    return True

# ✅ Bot Setup
app = ApplicationBuilder().token(telegram_bot_token).build()

app.add_handler(CommandHandler('start', start_command))
app.add_handler(CommandHandler('ask', ask_command))
app.add_handler(CommandHandler('image', image_command))
app.add_handler(CommandHandler('help', help_command))

logging.info("🤖 AI Bot is now running...")
app.run_polling()
