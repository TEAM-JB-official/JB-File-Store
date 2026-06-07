from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import config

client = AsyncIOMotorClient(config.Config.MONGODB_URI)
db = client[config.Config.DB_NAME]

# Collections
users_col = db["users"]
files_col = db["files"]
clones_col = db["clones"]
batches_col = db["batches"]
links_col = db["links"]
premium_col = db["premium"]
redeem_codes_col = db["redeem_codes"]
stats_col = db["stats"]
broadcast_col = db["broadcast"]
settings_col = db["settings"]

class Database:
    @staticmethod
    async def get_user(user_id: int) -> Optional[Dict]:
        return await users_col.find_one({"user_id": user_id})
    
    @staticmethod
    async def create_user(user_id: int, username: str = None, first_name: str = None):
        if not await users_col.find_one({"user_id": user_id}):
            await users_col.insert_one({
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "joined_date": datetime.utcnow(),
                "is_banned": False,
                "is_premium": False,
                "premium_expiry": None,
                "referral_by": None,
                "referral_count": 0,
                "daily_last_claim": None,
                "balance": 0,
                "total_links": 0,
                "total_views": 0
            })
    
    @staticmethod
    async def ban_user(user_id: int):
        await users_col.update_one({"user_id": user_id}, {"$set": {"is_banned": True}})
    
    @staticmethod
    async def unban_user(user_id: int):
        await users_col.update_one({"user_id": user_id}, {"$set": {"is_banned": False}})
    
    @staticmethod
    async def add_premium(user_id: int, days: int):
        user = await users_col.find_one({"user_id": user_id})
        current_expiry = user.get("premium_expiry") if user else None
        if current_expiry and current_expiry > datetime.utcnow():
            new_expiry = current_expiry + timedelta(days=days)
        else:
            new_expiry = datetime.utcnow() + timedelta(days=days)
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": True, "premium_expiry": new_expiry}}
        )
    
    @staticmethod
    async def remove_premium(user_id: int):
        await users_col.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": False, "premium_expiry": None}}
        )
    
    @staticmethod
    async def save_file(file_id: str, file_unique_id: str, user_id: int, file_name: str, file_size: int, mime_type: str, caption: str = None):
        result = await files_col.insert_one({
            "file_id": file_id,
            "file_unique_id": file_unique_id,
            "user_id": user_id,
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "caption": caption,
            "created_at": datetime.utcnow(),
            "views": 0,
            "clicks": 0
        })
        await users_col.update_one({"user_id": user_id}, {"$inc": {"total_links": 1}})
        return result.inserted_id
    
    @staticmethod
    async def get_file(file_id: str):
        return await files_col.find_one({"file_id": file_id})
    
    @staticmethod
    async def increment_views(file_id: str):
        await files_col.update_one({"file_id": file_id}, {"$inc": {"views": 1}})
    
    # Clone management
    @staticmethod
    async def register_clone(token: str, creator_id: int, bot_username: str) -> str:
        clone_id = f"clone_{creator_id}_{datetime.utcnow().timestamp()}"
        await clones_col.insert_one({
            "clone_id": clone_id,
            "token": token,
            "creator_id": creator_id,
            "bot_username": bot_username,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "settings": {}  # Separate settings for each clone
        })
        return clone_id
    
    @staticmethod
    async def get_clone(clone_id: str = None, token: str = None):
        if clone_id:
            return await clones_col.find_one({"clone_id": clone_id})
        if token:
            return await clones_col.find_one({"token": token})
        return None
    
    @staticmethod
    async def get_user_clones(creator_id: int):
        cursor = clones_col.find({"creator_id": creator_id})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def update_clone_status(clone_id: str, is_active: bool):
        await clones_col.update_one({"clone_id": clone_id}, {"$set": {"is_active": is_active}})
    
    @staticmethod
    async def delete_clone(clone_id: str):
        await clones_col.delete_one({"clone_id": clone_id})
    
    # Settings
    @staticmethod
    async def get_settings(clone_id: str = "main"):
        doc = await settings_col.find_one({"_id": clone_id})
        if not doc:
            default_settings = {
                "_id": clone_id,
                "link_shortener": False,
                "token_verification": False,
                "force_subscribe": None,
                "multiple_force_subscribe": [],
                "custom_caption": None,
                "custom_buttons": [],
                "auto_delete": False,
                "protect_content": False,
                "file_forward_lock": False,
                "disable_save_media": False,
                "disable_forward_media": False,
                "custom_start_message": None,
                "custom_about_message": None,
                "custom_thumbnail": None,
                "custom_welcome_photo": None,
                "custom_verification_message": None,
                "custom_join_message": None,
                "custom_success_message": None,
                "custom_deep_link_message": None
            }
            await settings_col.insert_one(default_settings)
            return default_settings
        return doc
    
    @staticmethod
    async def update_setting(clone_id: str, key: str, value):
        await settings_col.update_one({"_id": clone_id}, {"$set": {key: value}})
