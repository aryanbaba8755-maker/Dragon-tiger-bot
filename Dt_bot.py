import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler

# --- GLOBAL VARIABLES & CONFIG ---
OWNER_ID = 2107169286  
CURRENT_MODE = 'random' 

# --- CARD ENGINE LOGIC ---
SUITS = ['♠️', '♥️', '♣️', '♦️']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

def get_cards(mode):
    deck = [(r, s) for r in RANKS for s in SUITS]
    while True:
        c1, c2 = random.sample(deck, 2)
        val1, val2 = VALUES[c1[0]], VALUES[c2[0]]
        
        if mode == 'dragon_win':
            if val1 > val2: return c1, c2
            elif val2 > val1: return c2, c1
        elif mode == 'tiger_win':
            if val1 < val2: return c1, c2
            elif val2 < val1: return c2, c1
        else:
            return c1, c2

# --- SECURITY CHECKS ---
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.from_user:
        return False
        
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    if update.message.chat.type in ['group', 'supergroup']:
        try:
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != 'administrator':
                return False

            if user_id == OWNER_ID: return True
            
            user_member = await context.bot.get_chat_member(chat_id, user_id)
            return user_member.status in ['administrator', 'creator']
        except Exception:
            return False
    else:
        return user_id == OWNER_ID

async def track_bot_additions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result.new_chat_member.status in ["member", "administrator"]:
        added_by = result.from_user.id
        chat_id = result.chat.id
        if added_by != OWNER_ID:
            await context.bot.leave_chat(chat_id)

async def check_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    if left_member and left_member.id == OWNER_ID:
        try:
            await context.bot.leave_chat(update.message.chat_id)
        except Exception:
            pass

# --- OWNER SPECIAL COMMANDS ---
async def dwin_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if update.message.from_user.id != OWNER_ID: return 
    CURRENT_MODE = 'dragon_win'
    await update.message.reply_text("✅ Dragon Win Mode Active")

async def twin_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if update.message.from_user.id != OWNER_ID: return 
    CURRENT_MODE = 'tiger_win'
    await update.message.reply_text("✅ Tiger Win Mode Active")

async def dtrandom_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if update.message.from_user.id != OWNER_ID: return 
    CURRENT_MODE = 'random'
    await update.message.reply_text("✅ Random Mode Active")

# --- MAIN PLAY COMMAND ---
async def play_dt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return
    dragon_card, tiger_card = get_cards(CURRENT_MODE)
    msg = f"🐉 {dragon_card[0]}{dragon_card[1]}\n---------\n🐅 {tiger_card[0]}{tiger_card[1]}"
    await update.message.reply_text(msg)

def main():
    TOKEN = "8875864387:AAHYLurttiZ7XzD1AZnrPHE3K_ZyMAunhPs" # APNA ASLI TOKEN YAHAN DAALEIN
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("dt", play_dt))
    application.add_handler(CommandHandler("dwin", dwin_mode))
    application.add_handler(CommandHandler("twin", twin_mode))
    application.add_handler(CommandHandler("dtrandom", dtrandom_mode))
    
    application.add_handler(ChatMemberHandler(track_bot_additions, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, check_left_member))

    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

Isme kya change krna hai
