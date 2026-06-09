import requests
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = '8822336512:AAGckx_QRYKCeNoxVctg6rkEojDO_lDJgtg'
API_KEY = "nxa_a5981d47fcecb4f89a16bc469d61c503c02d9180" 
BASE_URL = "http://63.141.255.227/api/v1"
HEADERS = {"X-API-Key": API_KEY}
CHANNELS = ["@methadchannnel", "@otpgroupbabai"]
ADMIN_USERNAME = "babaiigc900179"
TARGET_GROUP_ID = "-1002242139049" 

verified_users = set()

# --- UI HELPER ---
def get_simple_ui(number, otp=None):
    status = f"🔢 OTP: `{otp}`" if otp else "⏳ Waiting for OTP..."
    return (f"🇬🇳 *GUINEA NUMBER*\n\n┏━━━━━━━━━━━━━━━━┓\n      `{number}`\n┗━━━━━━━━━━━━━━━━┛\n\n{status}")

async def is_subscribed(context, user_id):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']: return False
        except: return False
    return True

# --- BOT LOGIC ---
async def start(update, context):
    kb = [[InlineKeyboardButton("✅ VERIFY & GET NUMBER", callback_data='verify_sub')]]
    await update.message.reply_text("👋 Welcome! Click below to get Guinea Number:", reply_markup=InlineKeyboardMarkup(kb))

async def fetch_guinea_number(update, context):
    query = update.callback_query
    await query.edit_message_text("🔍 *Fetching Guinea Number...*")
    
    try:
        # FIXED: Sirf Guinea (GN) ke liye request
        payload = {"service": "google", "country": "GN", "engine": 1}
        resp = requests.post(f"{BASE_URL}/numbers/get", json=payload, headers=HEADERS).json()
        
        if resp.get("success"):
            num = resp['number']
            num_id = resp['number_id']
            await query.edit_message_text(get_simple_ui(num), parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Menu", callback_data='start_menu')]]))
            asyncio.create_task(poll_otp(context, query.message.chat_id, query.message.message_id, num_id, num))
        else:
            await query.edit_message_text("❌ *No Guinea numbers available right now.*", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Try Again", callback_data='verify_sub')]]))
    except Exception as e:
        await query.edit_message_text(f"Error: {e}")

async def poll_otp(context, chat_id, message_id, number_id, number):
    for _ in range(60):
        try:
            resp = requests.get(f"{BASE_URL}/numbers/{number_id}/sms", headers=HEADERS).json()
            if resp.get("success") and resp.get("sms"):
                otp = resp["sms"][0]["otp"]
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=get_simple_ui(number, otp), parse_mode='Markdown')
                await context.bot.send_message(chat_id=TARGET_GROUP_ID, text=f"📩 *Guinea OTP:* `{otp}`", parse_mode='Markdown')
                return
        except: pass
        await asyncio.sleep(5)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'verify_sub':
        if await is_subscribed(context, query.from_user.id):
            await fetch_guinea_number(update, context)
        else:
            await query.answer("❌ Join channels first!", show_alert=True)
    elif query.data == 'start_menu':
        await start(update, context) # Simplified menu

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is ready for Guinea!")
    app.run_polling()
        
