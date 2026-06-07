from telegram import Update, Message, InputMedia
from telegram.ext import ContextTypes
import config
from database import Database
from utils import format_size
import logging

logger = logging.getLogger(__name__)

class FileStorage:
    @staticmethod
    async def store_file(message: Message, user_id: int) -> str:
        """Store file in channel and return file_id"""
        if not config.Config.STORAGE_CHANNEL_ID:
            raise ValueError("Storage channel not configured")
        
        # Forward to storage channel
        forwarded = await message.forward(config.Config.STORAGE_CHANNEL_ID)
        
        # Get file details
        if forwarded.document:
            file_id = forwarded.document.file_id
            file_unique_id = forwarded.document.file_unique_id
            file_name = forwarded.document.file_name
            file_size = forwarded.document.file_size
            mime_type = forwarded.document.mime_type
            caption = forwarded.caption
        elif forwarded.video:
            file_id = forwarded.video.file_id
            file_unique_id = forwarded.video.file_unique_id
            file_name = forwarded.video.file_name or "video.mp4"
            file_size = forwarded.video.file_size
            mime_type = "video/mp4"
            caption = forwarded.caption
        elif forwarded.audio:
            file_id = forwarded.audio.file_id
            file_unique_id = forwarded.audio.file_unique_id
            file_name = forwarded.audio.file_name or "audio.mp3"
            file_size = forwarded.audio.file_size
            mime_type = "audio/mpeg"
            caption = forwarded.caption
        else:
            raise ValueError("Unsupported file type")
        
        # Save to database
        await Database.save_file(
            file_id=file_id,
            file_unique_id=file_unique_id,
            user_id=user_id,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            caption=caption
        )
        
        return file_id
    
    @staticmethod
    async def retrieve_file(context: ContextTypes.DEFAULT_TYPE, file_id: str, chat_id: int, password: str = None, one_time: bool = False):
        """Send file from storage to user"""
        file_data = await Database.get_file(file_id)
        if not file_data:
            await context.bot.send_message(chat_id, "❌ File not found")
            return
        
        # Check one-time link
        if one_time:
            await Database.delete_file(file_id)
        
        # Get settings for caption/buttons
        settings = await Database.get_settings()
        
        caption = file_data.get("caption", "")
        if settings.get("custom_caption"):
            caption = settings["custom_caption"].format(
                filename=file_data["file_name"],
                size=format_size(file_data["file_size"]),
                views=file_data["views"]+1
            )
        
        # Send file
        try:
            await context.bot.send_document(
                chat_id=chat_id,
                document=file_data["file_id"],
                caption=caption,
                protect_content=settings.get("protect_content", False)
            )
            await Database.increment_views(file_id)
        except Exception as e:
            logger.error(f"Error retrieving file: {e}")
            await context.bot.send_message(chat_id, "❌ Failed to send file")
