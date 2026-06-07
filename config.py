import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME", "file_store_bot")
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0)) if os.getenv("LOG_CHANNEL_ID") else None
    STORAGE_CHANNEL_ID = int(os.getenv("STORAGE_CHANNEL_ID", 0)) if os.getenv("STORAGE_CHANNEL_ID") else None
    DEFAULT_LINK_EXPIRY = int(os.getenv("DEFAULT_LINK_EXPIRY", 30))
    MAX_CLONES = int(os.getenv("MAX_CLONES", 100))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", 10))
    FLOOD_LIMIT = int(os.getenv("FLOOD_LIMIT", 10))
    FLOOD_PERIOD = int(os.getenv("FLOOD_PERIOD", 60))
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # URL Shortener APIs (optional)
    SHORTENER_API = os.getenv("SHORTENER_API", "")
    SHORTENER_URL = os.getenv("SHORTENER_URL", "")
    
    # Payment (dummy integration)
    PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
    
    # Premium Plan Prices (in INR or USD cents)
    PREMIUM_PRICES = {
        "weekly": 50,
        "monthly": 150,
        "yearly": 1500
    }
