import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID", "2040"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    OWNER_ID = int(os.getenv("OWNER_ID", "8643636559"))
    OWNER_USERNAME = "@xnwam"
    UPDATE_CHANNEL = "https://t.me/Soso_vor"
    UPDATE_CHANNEL_ID = int(os.getenv("UPDATE_CHANNEL_ID", "-1001234567890"))
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = "soso_bot"
    BOT_NAME = "𝐒𝐎𝐒𝐎"
    BOT_USERNAME = "@Soso_Ar_Bot"
