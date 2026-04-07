import sqlite3
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURATION ---
# GANTI BOT_TOKEN ini dengan token baru dari BotFather untuk Play77!
BOT_TOKEN = "7769504173:AAEN4iX_fdraTn1SPIXsYvIVx2mJLWKorhA" 
ADMIN_ID_STR = "6949823483"
ADMIN_ID = int(ADMIN_ID_STR)

logging.basicConfig(level=logging.INFO)

# --- DATABASE SETUP ---
# Menggunakan nama database play77.db agar tidak campur dengan bot lain
conn = sqlite3.connect("play77.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER
)
""")
conn.commit()

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Get referral ID from link (t.me/bot?start=123)
    ref = None
    if context.args:
        try:
            ref = int(context.args[0])
            if ref == user_id:  # Prevent self-referral
                ref = None
        except ValueError:
            ref = None

    # Save new user to database if not exists
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, ref))
        conn.commit()

    # Menu Buttons (Sudah dimodifikasi untuk Play77)
    keyboard = [
        [
            InlineKeyboardButton("🆕 Register Account", url="https://play77au.com/register/SMSRegister"), 
            InlineKeyboardButton("🔐 Login to Play", url="https://play77au.com/login")
        ],
        [
            InlineKeyboardButton("🎁 Bonuses", url="https://play77au.com/promotion"),        ],
        [
            InlineKeyboardButton("📢 Play77 VIP", url="https://play77au.com/vip"),
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/Play77Aus") 
        ],
        [
            InlineKeyboardButton("📱 Facebook", url="https://www.facebook.com/profile.php?id=61566445831810/"),
            InlineKeyboardButton("🆘 Support", url="https://play77au.com/chatroom")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Tampilan Pesan Sambutan Play77
    welcome_msg = (
        f"🎊 *WELCOME TO PLAY77 AUSTRALIA* 🎊\n\n"
        f"G'day, *{user.first_name}*! 🇦🇺\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *WHY CHOOSE PLAY77?* 🔥\n\n"
        "✅ *$10 AUD* MINIMUM DEPOSIT\n"
        "🚀 *ULTRA FAST* PAYID WITHDRAW\n"
        "🪙 *ALL MAJOR* CRYPTO ACCEPTED\n"
        "🤑 *CLAIM* YOUR DAILY REWARDS!\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

# --- ADMIN COMMANDS ---

async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    await update.message.reply_text(f"👥 Total users in Play77: {total}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /broadcast [message]")
        return

    msg_text = " ".join(context.args)
    cursor.execute("SELECT user_id FROM users")
    all_users = cursor.fetchall()

    sent = 0
    failed = 0
    for (uid,) in all_users:
        try:
            await context.bot.send_message(chat_id=uid, text=msg_text)
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"✅ Broadcast Complete!\nSent: {sent}\nFailed: {failed}")

# --- MAIN ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("users", users_count))
    application.add_handler(CommandHandler("broadcast", broadcast))

    print("--- PLAY77 BOT IS RUNNING ---")
    application.run_polling()
