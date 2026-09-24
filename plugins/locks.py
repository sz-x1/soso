from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from database import get_group, update_group, add_group

LOCKS = {
    "الروابط": "links", "الكلايش": "stickers", "الكيبورد": "keyboard",
    "الاغاني": "songs", "المتحركه": "gifs", "الملفات": "files",
    "الدردشه": "chat", "الفيديو": "video", "الصور": "photos",
    "المعرفات": "usernames", "التاك": "mention", "البوتات": "bots",
    "الانلاين": "inline", "التوجيه": "forward", "الكتم": "mute",
    "الكل": "all", "التحويل": "convert", "الاقتباسات": "quotes",
}

async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@Client.on_message(filters.group & filters.command(["قفل", "lock"]))
async def lock_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    if len(message.command) < 2:
        return await message.reply(f"❌ اكتب: /قفل [النوع]\nالأنواع: {'، '.join(LOCKS.keys())}")
    name = message.command[1]
    if name not in LOCKS:
        return await message.reply("❌ النوع ماشي موجود")
    group = await get_group(message.chat.id)
    if not group:
        await add_group(message.chat.id, message.chat.title)
        group = await get_group(message.chat.id)
    locks = group.get("locks", {})
    locks[LOCKS[name]] = True
    await update_group(message.chat.id, "locks", locks)
    await message.reply(f"🔒 تم قفل {name}")

@Client.on_message(filters.group & filters.command(["فتح", "unlock"]))
async def unlock_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    if len(message.command) < 2:
        return await message.reply(f"❌ اكتب: /فتح [النوع]\nالأنواع: {'، '.join(LOCKS.keys())}")
    name = message.command[1]
    if name not in LOCKS:
        return await message.reply("❌ النوع ماشي موجود")
    group = await get_group(message.chat.id)
    if not group:
        return await message.reply("❌ البوت ماشي مفعل")
    locks = group.get("locks", {})
    locks[LOCKS[name]] = False
    await update_group(message.chat.id, "locks", locks)
    await message.reply(f"🔓 تم فتح {name}")

@Client.on_message(filters.group & filters.command(["قفل الكل", "lockall"]))
async def lock_all(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    group = await get_group(message.chat.id)
    if not group:
        await add_group(message.chat.id, message.chat.title)
    locks = {v: True for v in LOCKS.values()}
    await update_group(message.chat.id, "locks", locks)
    await message.reply("🔒 تم قفل الكل")

@Client.on_message(filters.group & filters.command(["فتح الكل", "unlockall"]))
async def unlock_all(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    locks = {v: False for v in LOCKS.values()}
    await update_group(message.chat.id, "locks", locks)
    await message.reply("🔓 تم فتح الكل")

@Client.on_message(filters.group & filters.command(["الاقفال", "locks"]))
async def list_locks(client, message: Message):
    group = await get_group(message.chat.id)
    if not group:
        return await message.reply("❌ البوت ماشي مفعل")
    locks = group.get("locks", {})
    text = "🔐 الأقفال:\n\n"
    for name, key in LOCKS.items():
        text += f"{'🔒' if locks.get(key, False) else '🔓'} {name}\n"
    await message.reply(text)

@Client.on_message(filters.group, group=20)
async def locks_handler(client, message: Message):
    if not message.from_user:
        return
    group = await get_group(message.chat.id)
    if not group or not group.get("protection", False):
        return
    if await is_admin(client, message.chat.id, message.from_user.id):
        return
    locks = group.get("locks", {})
    try:
        if locks.get("all"):
            await message.delete()
            return
        if locks.get("links") and message.text and ("http" in message.text or "t.me" in message.text):
            await message.delete()
            return
        if locks.get("stickers") and message.sticker:
            await message.delete()
            return
        if locks.get("photos") and message.photo:
            await message.delete()
            return
        if locks.get("video") and message.video:
            await message.delete()
            return
        if locks.get("files") and message.document:
            await message.delete()
            return
        if locks.get("gifs") and message.animation:
            await message.delete()
            return
        if locks.get("forward") and message.forward_date:
            await message.delete()
            return
        if locks.get("bots") and message.from_user.is_bot:
            await message.delete()
            return
    except:
        pass
