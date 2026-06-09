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

user_status = {}
verified_users = set()

# --- UI & LOGIC HELPERS ---
def get_simple_ui(number, otp=None, country="GLOBAL"):
    status = f"🔢 OTP: `{otp}`" if otp else "⏳ Waiting for OTP..."
    return (
        f"🌐 *{country}*\n\n"
        "┏━━━━━━━━━━━━━━━━┓\n"
        f"      `{number}`\n"
        "┗━━━━━━━━━━━━━━━━┛\n\n"
        f"{status}"
    )

async def is_subscribed(context, user_id):
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']: return False
        except: return False
    return True

# --- HANDLERS ---
async def start(update, context):
    user_id = update.effective_user.id
    if user_id in verified_users:
        await update.message.reply_text("📱 *WELCOME TO PREMIUM BOT*", reply_markup=get_main_keyboard(), parse_mode='Markdown')
    else:
        kb = [
            [InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/methadchannnel")],
            [InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/otpgroupbabai")],
            [InlineKeyboardButton("✅ VERIFY", callback_data='verify_sub')]
        ]
        await update.message.reply_text("👋 Welcome! Pehle channels join karein:", reply_markup=InlineKeyboardMarkup(kb))

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Get Number", callback_data='get_number'), InlineKeyboardButton("📞 Support", callback_data='support')]
    ])

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'verify_sub':
        if await is_subscribed(context, query.from_user.id):
            verified_users.add(query.from_user.id)
            await query.edit_message_text("✅ *Verified!* Choose action:", reply_markup=get_main_keyboard(), parse_mode='Markdown')
        else:
            await query.answer("❌ Please join both channels first!", show_alert=True)
            
    elif query.data == 'get_number':
        user_status[query.message.chat_id] = "waiting_for_range"
        await query.edit_message_text("✍️ *Enter Number Range:*", parse_mode='Markdown')
    
    elif query.data == 'support':
        await query.edit_message_text("👤 *Admin Support:*", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")], [InlineKeyboardButton("⬅ Back", callback_data='back_to_main')]]), parse_mode='Markdown')
    
    elif query.data == 'back_to_main':
        await query.edit_message_text("📱 *Main Menu:*", reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def poll_otp(context, chat_id, message_id, number_id, number, country):
    for _ in range(60):
        try:
            resp = requests.get(f"{BASE_URL}/numbers/{number_id}/sms", headers=HEADERS).json()
            if resp.get("success") and resp.get("sms"):
                otp = resp["sms"][0]["otp"]
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=get_simple_ui(number, otp, country), parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back to Menu", callback_data='back_to_main')]]))
                await context.bot.send_message(chat_id=TARGET_GROUP_ID, text=f"📩 *{country} OTP:* `{otp}`", parse_mode='Markdown')
                return
        except: pass
        await asyncio.sleep(5)

# --- GLOBAL SEARCH UPDATED HANDLER ---
async def text_handler(update, context):
    chat_id = update.message.chat_id
    if user_status.get(chat_id) == "waiting_for_range":
        target_range = update.message.text.strip()
        user_status[chat_id] = None
        msg = await update.message.reply_text("🔍 *Searching Global Database...*", parse_mode='Markdown')
        
        found = False
        for _ in range(20): 
            try:
                # API ko 'country' batane ki zaroorat nahi, global search karega
                resp = requests.post(f"{BASE_URL}/numbers/get", json={"service": "google", "engine": 1}, headers=HEADERS).json()
                
                if resp.get("success") and resp.get("number", "").startswith(target_range):
                    num = resp['number']
                    await msg.edit_text(get_simple_ui(num, country="GLOBAL"), parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data='back_to_main')]]))
                    asyncio.create_task(poll_otp(context, chat_id, msg.message_id, resp['number_id'], num, "GLOBAL"))
                    found = True
                    break
            except: pass
            await asyncio.sleep(2)
        
        if not found: 
            await msg.edit_text("❌ No match found. Try another range.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data='back_to_main')]]))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Bot is ready!")
    app.run_polling()
            
