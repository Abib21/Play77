import sqlite3
import logging
import os
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "7769504173:AAEN4iX_fdraTn1SPIXsYvIVx2mJLWKorhA" 
ADMIN_ID_STR = "6949823483"
ADMIN_ID = int(ADMIN_ID_STR) if ADMIN_ID_STR else 0

logging.basicConfig(level=logging.INFO)

# --- DATABASE SETUP ---
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

    # 1. Get Australian Time (AEST/AEDT)
    au_tz = pytz.timezone('Australia/Sydney')
    au_time = datetime.now(au_tz).hour

    # 2. Auto Greeting Logic
    if 5 <= au_time < 12:
        greeting = "Good Morning"
    elif 12 <= au_time < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # 3. Referral & Database Logic
    ref = None
    if context.args:
        try:
            ref = int(context.args[0])
            if ref == user_id:
                ref = None
        except ValueError:
            ref = None

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, ref))
        conn.commit()

    # 4. Keyboard Setup
    keyboard = [
        [
            InlineKeyboardButton("🆕 Register Account", url="https://play77au.com/register/SMSRegister"), 
            InlineKeyboardButton("🔐 Login to Play", url="https://play77au.com/login")
        ],
        [
            InlineKeyboardButton("🎰 Play77 VIP", url="https://play77au.com/vip"),
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/Play77Aus") 
        ],
        [
            InlineKeyboardButton("📱 Facebook", url="https://www.facebook.com/profile.php?id=61566445831810"),
            InlineKeyboardButton("🆘 Support", url="https://play77au.com/chatroom")
        ],
        [
            # Expanded Bonus Button
            InlineKeyboardButton("🎁 Bonuses", url="https://play77au.com/promotion")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 5. Creative Welcome Message (Jackpot City Theme)
    welcome_msg = (
        "🎰  ✨  🍒  🔔  ✨  🎰\n"
        "✨ **PLAY77 AUSTRALIA** ✨\n"
        "🌃  🏙️  💎  🏙️  🌃\n\n"
        f"{greeting}, *{user.first_name.upper()}*! 👑🇦🇺\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 **URBAN JACKPOT FEATURES** 🔥\n\n"
        "🏙️  **DEPOSIT** ⇢  *$10 AUD*\n"
        "⚡  **PAYOUTS** ⇢  *INSTANT*\n"
        "🪙  **CRYPTO** ⇢  *BTC/ETH/SOL*\n"
        "🎁  **BONUSES** ⇢  *UNLIMITED*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🏙️  *The Heart of Australian Gaming* 🏙️\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⬇️ **SPIN TO WIN BELOW** ⬇️"
    )

    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

# --- ADMIN COMMANDS ---

async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE
