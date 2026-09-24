from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from database import get_group, update_group, add_group

async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def ensure_group(chat_id, title):
    group = await get_group(chat_id)
    if not group:
        await add_group(chat_id, title)
        group = await get_group(chat_id)
    return group

@Client.on_message(filters.group & filters.command(["تفعيل الاذكار", "azkar on"]))
async def azkar_on(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "azkar", True)
    await message.reply("✅ تم تفعيل الاذكار")

@Client.on_message(filters.group & filters.command(["تعطيل الاذكار", "azkar off"]))
async def azkar_off(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "azkar", False)
    await message.reply("❌ تم تعطيل الاذكار")

@Client.on_message(filters.group & filters.command(["تفعيل الردود", "reply on"]))
async def reply_on(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "reply", True)
    await message.reply("✅ تم تفعيل الردود")

@Client.on_message(filters.group & filters.command(["تعطيل الردود", "reply off"]))
async def reply_off(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "reply", False)
    await message.reply("❌ تم تعطيل الردود")

@Client.on_message(filters.group & filters.command(["تفعيل التحذير", "warn on"]))
async def warn_on(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "warn", True)
    await message.reply("✅ تم تفعيل التحذير")

@Client.on_message(filters.group & filters.command(["تعطيل التحذير", "warn off"]))
async def warn_off(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "warn", False)
    await message.reply("❌ تم تعطيل التحذير")

@Client.on_message(filters.group & filters.command(["تفعيل الحمايه", "protect on"]))
async def protect_on(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "protection", True)
    await message.reply("✅ تم تفعيل الحمايه")

@Client.on_message(filters.group & filters.command(["تعطيل الحمايه", "protect off"]))
async def protect_off(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "protection", False)
    await message.reply("❌ تم تعطيل الحمايه")

@Client.on_message(filters.group & filters.command(["تفعيل التحقق", "check on"]))
async def check_on(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "check", True)
    await message.reply("✅ تم تفعيل التحقق")

@Client.on_message(filters.group & filters.command(["تعطيل التحقق", "check off"]))
async def check_off(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await ensure_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "check", False)
    await message.reply("❌ تم تعطيل التحقق")
