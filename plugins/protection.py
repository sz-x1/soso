import re
from collections import defaultdict
from time import time
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from database import get_group, update_group, add_group

async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def get_target(client, message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            return await client.get_users(message.command[1])
        except:
            return None
    return None

# ====== فك الكتم ======
@Client.on_message(filters.group & filters.command(["فك الكتم", "unmute"]))
async def unmute_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.restrict_chat_member(
            message.chat.id, target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.reply(f"🔊 تم فك الكتم عن {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

# ====== فك الحظر ======
@Client.on_message(filters.group & filters.command(["فك الحظر", "unban"]))
async def unban_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"✅ تم فك الحظر عن {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

# ====== تحذير ======
@Client.on_message(filters.group & filters.command(["تحذير", "warn"]))
async def warn_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    group = await get_group(message.chat.id)
    if not group:
        await add_group(message.chat.id, message.chat.title)
        group = await get_group(message.chat.id)
    warns = group.get("warns", {})
    user_warns = warns.get(str(target.id), 0) + 1
    warns[str(target.id)] = user_warns
    await update_group(message.chat.id, "warns", warns)
    if user_warns >= 3:
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await message.reply(f"🚫 تم حظر {target.mention} بعد 3 تحذيرات")
            warns[str(target.id)] = 0
            await update_group(message.chat.id, "warns", warns)
        except:
            pass
    else:
        await message.reply(f"⚠️ تحذير {target.mention}\nالتحذيرات: {user_warns}/3")

# ====== مسح التحذيرات ======
@Client.on_message(filters.group & filters.command(["مسح التحذيرات", "resetwarns"]))
async def reset_warns(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    group = await get_group(message.chat.id)
    warns = group.get("warns", {}) if group else {}
    warns[str(target.id)] = 0
    await update_group(message.chat.id, "warns", warns)
    await message.reply(f"✅ تم مسح تحذيرات {target.mention}")

# ====== حماية من الروابط ======
LINK_PATTERN = re.compile(r"(https?://|t\.me/|telegram\.me/|www\.)")

@Client.on_message(filters.group, group=1)
async def antilink_handler(client, message: Message):
    if not message.from_user:
        return
    group = await get_group(message.chat.id)
    if not group or not group.get("protection", False):
        return
    if not group.get("antilink", True):
        return
    if await is_admin(client, message.chat.id, message.from_user.id):
        return
    text = message.text or message.caption or ""
    if not text:
        return
    if LINK_PATTERN.search(text):
        try:
            await message.delete()
            await client.restrict_chat_member(
                message.chat.id, message.from_user.id,
                ChatPermissions(can_send_messages=False)
            )
            await message.reply(f"🔇 تم كتم {message.from_user.mention} بسبب إرسال رابط")
        except:
            pass

# ====== تفعيل/تعطيل الروابط ======
@Client.on_message(filters.group & filters.command(["تفعيل الروابط", "antilink on"]))
async def enable_antilink(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "antilink", True)
    await message.reply("✅ تم تفعيل الحماية من الروابط")

@Client.on_message(filters.group & filters.command(["تعطيل الروابط", "antilink off"]))
async def disable_antilink(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "antilink", False)
    await message.reply("❌ تم تعطيل الحماية من الروابط")

# ====== حماية من السبام ======
SPAM_TRACKER = defaultdict(list)
SPAM_LIMIT = 5
SPAM_TIME = 5

@Client.on_message(filters.group, group=2)
async def antispam_handler(client, message: Message):
    if not message.from_user:
        return
    group = await get_group(message.chat.id)
    if not group or not group.get("protection", False):
        return
    if not group.get("antispam", True):
        return
    if await is_admin(client, message.chat.id, message.from_user.id):
        return
    user_id = message.from_user.id
    now = time()
    SPAM_TRACKER[user_id] = [t for t in SPAM_TRACKER[user_id] if now - t < SPAM_TIME]
    SPAM_TRACKER[user_id].append(now)
    if len(SPAM_TRACKER[user_id]) > SPAM_LIMIT:
        try:
            await client.restrict_chat_member(
                message.chat.id, user_id,
                ChatPermissions(can_send_messages=False)
            )
            await message.reply(f"🔇 تم كتم {message.from_user.mention} بسبب السبام")
            SPAM_TRACKER[user_id] = []
        except:
            pass

@Client.on_message(filters.group & filters.command(["تفعيل السبام", "antispam on"]))
async def enable_antispam(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "antispam", True)
    await message.reply("✅ تم تفعيل الحماية من السبام")

@Client.on_message(filters.group & filters.command(["تعطيل السبام", "antispam off"]))
async def disable_antispam(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "antispam", False)
    await message.reply("❌ تم تعطيل الحماية من السبام")

# ====== ترحيب ======
@Client.on_message(filters.group & filters.new_chat_members)
async def welcome_new(client, message: Message):
    group = await get_group(message.chat.id)
    if not group:
        await add_group(message.chat.id, message.chat.title)
        group = await get_group(message.chat.id)
    if not group.get("welcome", True):
        return
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        await message.reply(
            f"✨ أهلاً وسهلاً {member.mention}\n"
            f"🌸 نورت المجموعة {message.chat.title}\n"
            f"📖 اقرا القوانين قبل ما تشارك"
        )

@Client.on_message(filters.group & filters.command(["تفعيل الترحيب", "welcome on"]))
async def enable_welcome(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "welcome", True)
    await message.reply("✅ تم تفعيل الترحيب")

@Client.on_message(filters.group & filters.command(["تعطيل الترحيب", "welcome off"]))
async def disable_welcome(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    await update_group(message.chat.id, "welcome", False)
    await message.reply("❌ تم تعطيل الترحيب")
