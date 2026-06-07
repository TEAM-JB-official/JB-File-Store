from telegram import Bot
from database import Database
import asyncio

async def broadcast_message(bot: Bot, message: str):
    users = await Database.users_col.find({}, {"user_id": 1}).to_list(length=None)
    total = len(users)
    success = 0
    for user in users:
        try:
            await bot.send_message(user["user_id"], message)
            success += 1
            await asyncio.sleep(0.05)  # Avoid flood wait
        except:
            pass
    return total, success
