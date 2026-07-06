import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8875864387:AAGxw3ZuoxRfE5he4p4Gk5wsYJChOmX7cLg"
OWNER_ID = 2107169286  
CURRENT_MODE = 'random' 

# --- FLASK (Render Uptime) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- SECURITY CHECKS ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.message.from_user.id
    if user_id == OWNER_ID: return True
    
    # Check if user is Admin in the group
    chat_member = await context.bot.get_chat_member(update.message.chat_id, user_id)
    return chat_member.status in ['administrator', 'creator']

# --- ENGINE ---
def get_cards(mode):
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    VALUES = {r: i+1 for i, r in enumerate(RANKS)}
    SUITS = ['♠️', '♥️', '♣️', '♦️']
    deck = [(r, s) for r in RANKS for s in SUITS]
    while True:
        c1, c2 = random.sample(deck, 2)
        v1, v2 = VALUES[c1[0]], VALUES[c2[0]]
        if mode == 'dragon_win' and v1 > v2: return c1, c2
        if mode == 'tiger_win' and v2 > v1: return c1, c2
        if mode == 'random': return c1, c2

# --- COMMAND HANDLERS ---
async def track_bot_additions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result.new_chat_member.status in ["member", "administrator"]:
        if result.from_user.id != OWNER_ID:
            await context.bot.leave_chat(result.chat.id)

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    # Sirf Owner access
    if update.message.from_user.id != OWNER_ID: return 
    
    cmd = update.message.text.lower()
    if 'dwin' in cmd: CURRENT_MODE = 'dragon_win'
    elif 'twin' in cmd: CURRENT_MODE = 'tiger_win'
    else: CURRENT_MODE = 'random'
    await update.message.reply_text(f"✅ Mode: {CURRENT_MODE.replace('_', ' ').title()}")

async def play_dt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Owner aur Admin dono access
    if not await is_admin(update, context): return
    d, t = get_cards(CURRENT_MODE)
    await update.message.reply_text(f"🐉 {d[0]}{d[1]}\n🐅 {t[0]}{t[1]}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler(["dwin", "twin", "dtrandom"], set_mode))
    application.add_handler(CommandHandler("dt", play_dt))
    application.add_handler(ChatMemberHandler(track_bot_additions, ChatMemberHandler.MY_CHAT_MEMBER))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    main()
    
