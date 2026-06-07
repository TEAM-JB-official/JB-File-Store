import asyncio
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Tuple
from telegram import Update
from telegram.ext import ContextTypes
import config

# Rate Limiting
user_rate_limiter: Dict[int, list] = {}
flood_limiter: Dict[int, list] = {}

def check_rate_limit(user_id: int) -> Tuple[bool, int]:
    now = datetime.utcnow().timestamp()
    if user_id not in user_rate_limiter:
        user_rate_limiter[user_id] = []
    
    timestamps = user_rate_limiter[user_id]
    timestamps = [t for t in timestamps if now - t < config.Config.RATE_LIMIT_PERIOD]
    if len(timestamps) >= config.Config.RATE_LIMIT:
        return False, len(timestamps)
    
    timestamps.append(now)
    user_rate_limiter[user_id] = timestamps
    return True, len(timestamps)

def check_flood(user_id: int) -> bool:
    now = datetime.utcnow().timestamp()
    if user_id not in flood_limiter:
        flood_limiter[user_id] = []
    
    timestamps = flood_limiter[user_id]
    timestamps = [t for t in timestamps if now - t < config.Config.FLOOD_PERIOD]
    if len(timestamps) >= config.Config.FLOOD_LIMIT:
        return False
    
    timestamps.append(now)
    flood_limiter[user_id] = timestamps
    return True

def generate_unique_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

async def send_log(context: ContextTypes.DEFAULT_TYPE, text: str):
    if config.Config.LOG_CHANNEL_ID:
        await context.bot.send_message(config.Config.LOG_CHANNEL_ID, text)

def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
