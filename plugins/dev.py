from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["اذاعة", "broadcast"]))
async def broadcast(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ رد على رسالة باش تبعتها للكل")
    from database import users_col
    count = 0
    async for user in users_col.find({}):
        try:
            await message.reply_to_message.copy(user["user_id"])
            count += 1
        except:
            pass
    await message.reply(f"✅ تم الإرسال لـ {count} مستخدم")

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["احصائيات البوت", "botstats"]))
async def botstats(client, message: Message):
    from database import users_col, groups_col
    users = await users_col.count_documents({})
    groups = await groups_col.count_documents({})
    await message.reply(f"📊 **إحصائيات البوت:**\n\n• المستخدمين: {users}\n• المجموعات: {groups}")

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["اعادة تشغيل", "restart"]))
async def restart(client, message: Message):
    await message.reply("🔄 **جاري إعادة التشغيل...**")
    import os
    import sys
    os.execv(sys.executable, [sys.executable] + sys.argv)

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["ايقاف", "shutdown"]))
async def shutdown(client, message: Message):
    await message.reply("🛑 **جاري الإيقاف...**")
    import sys
    sys.exit(0)
