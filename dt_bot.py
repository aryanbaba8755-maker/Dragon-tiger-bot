import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8875864387:AAHYLurttiZ7XzD1AZnrPHE3K_ZyMAunhPs"
OWNER_ID = 2107169286  
CURRENT_MODE = 'random' 

# --- FLASK (Render Uptime) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ENGINE ---
def get_cards(mode):
    SUITS = ['♠️', '♥️', '♣️', '♦️']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
    deck = [(r, s) for r in RANKS for s in SUITS]
    
    while True:
        c1, c2 = random.sample(deck, 2)
        val1, val2 = VALUES[c1[0]], VALUES[c2[0]]
        if mode == 'dragon_win' and val1 > val2: return c1, c2
        if mode == 'tiger_win' and val1 < val2: return c2, c1
        if mode == 'random': return c1, c2

# --- SECURITY & LOGIC ---
async def track_bot_additions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result.new_chat_member.status in ["member", "administrator"]:
        if result.from_user.id != OWNER_ID:
            await context.bot.leave_chat(result.chat.id)

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if update.message.from_user.id != OWNER_ID: return 
    
    cmd = update.message.text.lower()
    if 'dwin' in cmd: CURRENT_MODE = 'dragon_win'
    elif 'twin' in cmd: CURRENT_MODE = 'tiger_win'
    else: CURRENT_MODE = 'random'
    
    await update.message.reply_text(f"✅ {CURRENT_MODE.replace('_', ' ').title()} Mode Active")

async def play_dt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dragon, tiger = get_cards(CURRENT_MODE)
    await update.message.reply_text(f"🐉 {dragon[0]}{dragon[1]}\n---------\n🐅 {tiger[0]}{tiger[1]}")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler(["dwin", "twin", "dtrandom"], set_mode))
    application.add_handler(CommandHandler("dt", play_dt))
    application.add_handler(ChatMemberHandler(track_bot_additions, ChatMemberHandler.MY_CHAT_MEMBER))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    main()
    
