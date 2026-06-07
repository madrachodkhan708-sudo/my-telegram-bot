from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# Yahan apna token aur username confirm kar lein
TOKEN = '8852095458:AAGErCCIZe4Iol1Gf8Izb5Z8BrNN_Cc6jdk'
ADMIN_USERNAME = "babaiigc900179"
UPI_ID = "Binay956@ptyes" 

# Global Variable
user_balance = 0

def get_main_menu():
    return [
        [InlineKeyboardButton("📱 Get Number", callback_data='get_number'),
         InlineKeyboardButton("💰 Deposit", callback_data='deposit')],
        [InlineKeyboardButton(f"💳 Balance: {user_balance} INR", callback_data='balance'),
         InlineKeyboardButton("📞 Support", callback_data='support')]
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Naya user notification logic
    user = update.effective_user
    admin_msg = (f"👤 *Naya User Aaya!*\n\nName: {user.first_name}\n"
                 f"ID: `{user.id}`\nUsername: @{user.username if user.username else 'N/A'}")
    
    # Notification admin ko bhejna (Agar admin ne bot start kiya hai)
    try:
        await context.bot.send_message(chat_id=ADMIN_USERNAME, text=admin_msg, parse_mode='Markdown')
    except:
        pass 

    await update.message.reply_text("**\n\n🐠 Click the Get Number button to receive your number!:", 
                                    reply_markup=InlineKeyboardMarkup(get_main_menu()), parse_mode='Markdown')

# ADMIN COMMAND
async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_balance
    if update.effective_user.username == ADMIN_USERNAME:
        try:
            amount = int(context.args[0])
            user_balance += amount
            await update.message.reply_text(f"✅ Successfully added {amount} INR!\nNew Balance: {user_balance} INR")
        except:
            await update.message.reply_text("❌ Usage: /addbalance [amount]")
    else:
        await update.message.reply_text("❌ Aap Admin nahi hain!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_balance
    query = update.callback_query
    await query.answer()

    if query.data == 'support':
        keyboard = [[InlineKeyboardButton("📩 Admin Message", url=f"t.me/{ADMIN_USERNAME}")],
                    [InlineKeyboardButton("⬅ Back", callback_data='back_to_main')]]
        await query.edit_message_text("👇 Contact Support:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'deposit':
        keyboard = [
            [InlineKeyboardButton("10 INR", callback_data="pay_10"), InlineKeyboardButton("20 INR", callback_data="pay_20")],
            [InlineKeyboardButton("30 INR", callback_data="pay_30"), InlineKeyboardButton("40 INR", callback_data="pay_40")],
            [InlineKeyboardButton("50 INR", callback_data="pay_50"), InlineKeyboardButton("60 INR", callback_data="pay_60")],
            [InlineKeyboardButton("70 INR", callback_data="pay_70"), InlineKeyboardButton("80 INR", callback_data="pay_80")],
            [InlineKeyboardButton("90 INR", callback_data="pay_90"), InlineKeyboardButton("100 INR", callback_data="pay_100")],
            [InlineKeyboardButton("⬅ Back to Menu", callback_data='back_to_main')]
        ]
        await query.edit_message_text("💰 Select Amount to Deposit:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('pay_'):
        amount = query.data.split('_')[1]
        text = f"Send {amount} INR to this UPI:\n\n`{UPI_ID}`\n\n✅ Payment karne ke baad 'Verify' par click karein."
        keyboard = [[InlineKeyboardButton("✅ Verify Payment", callback_data='verify')],
                    [InlineKeyboardButton("⬅ Back to Deposit", callback_data='deposit')]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'verify':
        await query.edit_message_text("⏳ *Pending Payment*\n\nAdmin will approve your payment soon.", parse_mode='Markdown',
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data='back_to_main')]]))

    elif query.data == 'get_number':
        if user_balance >= 20:
            user_balance -= 20
            keyboard = [[InlineKeyboardButton("🔵 Facebook", callback_data='fb_num'),
                         InlineKeyboardButton("📸 Instagram", callback_data='insta_num')],
                        [InlineKeyboardButton("⬅ Back to Menu", callback_data='back_to_main')]]
            await query.edit_message_text("✅ Payment Success! Choose Platform:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("❌ Insufficient Balance! Pehle Deposit karein.")

    elif query.data in ['fb_num', 'insta_num']:
        keyboard = [
            [InlineKeyboardButton("🔄 Replace Number", callback_data='replace'),
             InlineKeyboardButton("🌍 Change Country", callback_data='change_country')],
            [InlineKeyboardButton("📱 Otp Group Here", url='https://t.me/your_link'),
             InlineKeyboardButton("⬅ Back to Menu", callback_data='back_to_main')]
        ]
        message = (f"✅ *Number Assigned!*\n\n📱 Face-Insta | `959680015292` | Myanmar 🇲🇲\n\n⏳ *Wait, Stay here... OTP Coming Soon!*")
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'back_to_main':
        await query.edit_message_text("✅ *PROXY READY TO USE*\n\n👇 Select your option:", 
                                      reply_markup=InlineKeyboardMarkup(get_main_menu()), parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addbalance", add_balance_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot bilkul sahi chal raha hai!")
    app.run_polling()
      
