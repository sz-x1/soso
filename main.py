import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, idle
from config import Config

app = Client(
    "SosoBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    await app.start()
    me = await app.get_me()
    print(f"✅ البوت {me.first_name} خدام...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
