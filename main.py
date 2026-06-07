#!/usr/bin/env python3
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from telegram import Update
from handlers import user, admin, clone, file, settings
from database import Database
from clone_manager import clone_manager
from utils import send_log
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_chat:
        await context.bot.send_message(update.effective_chat.id, "⚠️ An error occurred. Please try again later.")

async def main():
    # Initialize database indices
    await Database.users_col.create_index("user_id", unique=True)
    await Database.files_col.create_index("file_id")
    await Database.clones_col.create_index("token", unique=True)
    await Database.clones_col.create_index("creator_id")
    
    # Create main bot application
    app = Application.builder().token(config.Config.BOT_TOKEN).build()
    
    # Add conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("link", file.link_command)],
        states={
            file.WAITING_FILE: [MessageHandler(filters.ALL, file.receive_file)],
        },
        fallbacks=[CommandHandler("cancel", file.cancel_conversation)]
    )
    app.add_handler(conv_handler)
    
    # Register command handlers
    app.add_handler(CommandHandler("start", user.start_command))
    app.add_handler(CommandHandler("help", user.help_command))
    app.add_handler(CommandHandler("id", user.id_command))
    app.add_handler(CommandHandler("about", user.about_command))
    app.add_handler(CommandHandler("link", file.link_command))
    app.add_handler(CommandHandler("batch", file.batch_command))
    app.add_handler(CommandHandler("custom_batch", file.custom_batch_command))
    app.add_handler(CommandHandler("multiple_batch", file.multiple_batch_command))
    app.add_handler(CommandHandler("special_link", file.special_link_command))
    app.add_handler(CommandHandler("settings", settings.settings_command))
    app.add_handler(CommandHandler("clone", clone.clone_command))
    app.add_handler(CommandHandler("activate", clone.activate_command))
    app.add_handler(CommandHandler("delete", clone.delete_command))
    
    # Admin commands
    app.add_handler(CommandHandler("broadcast", admin.broadcast_command))
    app.add_handler(CommandHandler("stats", admin.stats_command))
    app.add_handler(CommandHandler("ban", admin.ban_command))
    app.add_handler(CommandHandler("unban", admin.unban_command))
    app.add_handler(CommandHandler("premium", admin.premium_command))
    app.add_handler(CommandHandler("users", admin.users_command))
    app.add_handler(CommandHandler("backup", admin.backup_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(settings.settings_callback, pattern="^set_"))
    app.add_handler(CallbackQueryHandler(clone.clone_callback, pattern="^clone_"))
    app.add_handler(CallbackQueryHandler(user.menu_callback, pattern="^back_"))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start main bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("Main bot started")
    
    # Load existing clones from database
    clones = await Database.clones_col.find({"is_active": True}).to_list(length=None)
    for clone_data in clones:
        try:
            await clone_manager.start_clone(clone_data["clone_id"], clone_data["token"])
        except Exception as e:
            logger.error(f"Failed to start clone {clone_data['clone_id']}: {e}")
    
    # Keep bot running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        for clone_id in list(clone_manager.applications.keys()):
            await clone_manager.stop_clone(clone_id)

if __name__ == "__main__":
    asyncio.run(main())
