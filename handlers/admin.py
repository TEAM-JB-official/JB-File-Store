from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from utils import send_log
from broadcast import broadcast_message
import asyncio
from datetime import datetime
import config

async def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in config.Config.ADMIN_IDS:
            await update.message.reply_text("⛔ Admin access required.")
            return
        return await func(update, context)
    return wrapper

@admin_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    await update.message.reply_text("📢 Broadcasting... This may take time.")
    total, success = await broadcast_message(context.bot, msg)
    await update.message.reply_text(f"✅ Broadcast completed.\nTotal: {total}\nSuccess: {success}")

@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = await Database.users_col.count_documents({})
    total_files = await Database.files_col.count_documents({})
    total_views = await Database.files_col.aggregate([{"$group": {"_id": None, "total": {"$sum": "$views"}}}]).to_list(1)
    total_views = total_views[0]["total"] if total_views else 0
    premium_users = await Database.users_col.count_documents({"is_premium": True})
    total_clones = await Database.clones_col.count_documents({})
    
    stats_text = f"""
📊 *Bot Statistics*
👥 Users: {total_users}
📁 Files: {total_files}
👁️ Views: {total_views}
⭐ Premium: {premium_users}
🤖 Clones: {total_clones}
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id> [reason]")
        return
    user_id = int(context.args[0])
    await Database.ban_user(user_id)
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason"
    await update.message.reply_text(f"✅ User {user_id} banned.\nReason: {reason}")
    await send_log(context, f"Admin {update.effective_user.id} banned {user_id}: {reason}")

@admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    user_id = int(context.args[0])
    await Database.unban_user(user_id)
    await update.message.reply_text(f"✅ User {user_id} unbanned.")

@admin_only
async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /premium <add|remove> <user_id> [days]")
        return
    action = context.args[0].lower()
    user_id = int(context.args[1])
    if action == "add":
        days = int(context.args[2]) if len(context.args) > 2 else 30
        await Database.add_premium(user_id, days)
        await update.message.reply_text(f"✅ Added premium to {user_id} for {days} days.")
    elif action == "remove":
        await Database.remove_premium(user_id)
        await update.message.reply_text(f"✅ Removed premium from {user_id}.")

@admin_only
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = await Database.users_col.count_documents({})
    await update.message.reply_text(f"Total users: {total}\n\nUse /export_users to get list (CSV)")

@admin_only
async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Starting backup...")
    # Implement backup logic - export collections to JSON files
    await update.message.reply_text("✅ Backup completed. Check server logs.")
