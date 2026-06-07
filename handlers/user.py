from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from keyboards import main_menu
from utils import check_rate_limit, check_flood, send_log
import config

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await Database.create_user(user.id, user.username, user.first_name)
    
    # Deep link handling for file retrieval
    if context.args and context.args[0].startswith("file_"):
        file_id = context.args[0][5:]
        await handle_file_retrieval(update, context, file_id)
        return
    
    # Check if user is banned
    user_data = await Database.get_user(user.id)
    if user_data and user_data.get("is_banned"):
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    settings = await Database.get_settings(context.bot_data.get("clone_id", "main"))
    welcome_msg = settings.get("custom_start_message") or f"Welcome {user.first_name}!\nI can store files permanently and generate shareable links."
    
    photo = settings.get("custom_welcome_photo")
    if photo:
        await update.message.reply_photo(photo=photo, caption=welcome_msg, reply_markup=main_menu())
    else:
        await update.message.reply_text(welcome_msg, reply_markup=main_menu())
    
    await send_log(context, f"New user: {user.id} - @{user.username}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *Available Commands*

/file - Store a file permanently
/batch - Store consecutive messages
/custom_batch - Select specific messages
/multiple_batch - Create multiple batches
/special_link - Link with expiry/limits
/id - Show your user ID
/settings - Configure bot settings
/clone - Create your own clone bot
/activate - Activate a clone
/delete - Delete a clone

*Admin Commands*
/broadcast, /stats, /ban, /unban, /premium, /users, /backup

Join our channel for updates!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = f"👤 Your User ID: `{user.id}`\n"
    if chat.type != "private":
        text += f"💬 Chat ID: `{chat.id}`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = await Database.get_settings(context.bot_data.get("clone_id", "main"))
    about_text = settings.get("custom_about_message") or """
🤖 *Permanent File Store Bot*

Store files permanently in Telegram and generate shareable links with advanced features:
• Password protection
• Expiry dates
• View limits
• One-time links
• Clone bot support

Made with ❤️
    """
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def handle_file_retrieval(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str):
    user = update.effective_user
    # Check rate limit
    allowed, _ = check_rate_limit(user.id)
    if not allowed:
        await update.message.reply_text("⏳ Rate limit exceeded. Please wait.")
        return
    
    # Check flood
    if not check_flood(user.id):
        await update.message.reply_text("🚫 Flood detected. Please slow down.")
        return
    
    # Check force subscribe
    settings = await Database.get_settings(context.bot_data.get("clone_id", "main"))
    if settings.get("force_subscribe"):
        try:
            member = await context.bot.get_chat_member(settings["force_subscribe"], user.id)
            if member.status in ["left", "kicked"]:
                join_btn = InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{settings['force_subscribe'].replace('@','')}")
                await update.message.reply_text(
                    "🔒 Please join our channel first to access files.",
                    reply_markup=InlineKeyboardMarkup([[join_btn]])
                )
                return
        except:
            pass
    
    # Retrieve file from storage
    from storage import FileStorage
    await FileStorage.retrieve_file(context, file_id, update.effective_chat.id)
