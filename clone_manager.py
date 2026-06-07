import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import InvalidToken
import config
from database import Database
from handlers.user import start_command, help_command, id_command
from handlers.file import link_command, batch_command, custom_batch_command, multiple_batch_command, special_link_command
from handlers.settings import settings_command, settings_callback
import logging

logger = logging.getLogger(__name__)

class CloneManager:
    def __init__(self):
        self.applications = {}  # clone_id -> Application
        self.tasks = {}  # clone_id -> asyncio.Task
    
    async def start_clone(self, clone_id: str, token: str):
        """Start a clone bot instance"""
        if clone_id in self.applications:
            await self.stop_clone(clone_id)
        
        # Create application
        app = Application.builder().token(token).build()
        
        # Add handlers (same as main bot but with clone context)
        app.add_handler(CommandHandler("start", self.clone_start_handler(clone_id)))
        app.add_handler(CommandHandler("help", self.clone_help_handler(clone_id)))
        app.add_handler(CommandHandler("id", self.clone_id_handler(clone_id)))
        app.add_handler(CommandHandler("link", self.clone_link_handler(clone_id)))
        app.add_handler(CommandHandler("batch", self.clone_batch_handler(clone_id)))
        app.add_handler(CommandHandler("custom_batch", self.clone_custom_batch_handler(clone_id)))
        app.add_handler(CommandHandler("multiple_batch", self.clone_multiple_batch_handler(clone_id)))
        app.add_handler(CommandHandler("special_link", self.clone_special_link_handler(clone_id)))
        app.add_handler(CommandHandler("settings", self.clone_settings_handler(clone_id)))
        app.add_handler(CallbackQueryHandler(self.clone_callback_handler(clone_id)))
        
        # Start polling
        self.applications[clone_id] = app
        task = asyncio.create_task(app.run_polling())
        self.tasks[clone_id] = task
        
        logger.info(f"Clone {clone_id} started")
        return True
    
    async def stop_clone(self, clone_id: str):
        """Stop a clone bot instance"""
        if clone_id in self.applications:
            app = self.applications[clone_id]
            await app.updater.stop()
            await app.stop()
            if clone_id in self.tasks:
                self.tasks[clone_id].cancel()
            del self.applications[clone_id]
            del self.tasks[clone_id]
            logger.info(f"Clone {clone_id} stopped")
    
    # Wrapper handlers that pass clone_id to actual handlers
    def clone_start_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await start_command(update, context)
        return handler
    
    def clone_help_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await help_command(update, context)
        return handler
    
    def clone_id_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await id_command(update, context)
        return handler
    
    def clone_link_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await link_command(update, context)
        return handler
    
    def clone_batch_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await batch_command(update, context)
        return handler
    
    def clone_custom_batch_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await custom_batch_command(update, context)
        return handler
    
    def clone_multiple_batch_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await multiple_batch_command(update, context)
        return handler
    
    def clone_special_link_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await special_link_command(update, context)
        return handler
    
    def clone_settings_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await settings_command(update, context)
        return handler
    
    def clone_callback_handler(self, clone_id):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            context.bot_data["clone_id"] = clone_id
            await settings_callback(update, context)
        return handler

clone_manager = CloneManager()
