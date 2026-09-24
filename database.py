from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

client = AsyncIOMotorClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

users_col = db["users"]
groups_col = db["groups"]
force_channels_col = db["force_channels"]
whispers_col = db["whispers"]

async def add_user(user_id, first_name, username=None):
    if not await users_col.find_one({"user_id": user_id}):
        await users_col.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "username": username
        })

async def get_user(user_id):
    return await users_col.find_one({"user_id": user_id})

async def add_group(chat_id, title):
    if not await groups_col.find_one({"chat_id": chat_id}):
        await groups_col.insert_one({
            "chat_id": chat_id,
            "title": title,
            "welcome": True,
            "protection": True
        })

async def get_group(chat_id):
    return await groups_col.find_one({"chat_id": chat_id})

async def update_group(chat_id, key, value):
    await groups_col.update_one(
        {"chat_id": chat_id},
        {"$set": {key: value}}
    )
