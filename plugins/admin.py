from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from pyrogram.enums import ChatMemberStatus

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

RANKS = {
    "مالك": ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=True, can_change_info=True, can_invite_users=True, can_pin_messages=True),
    "مشرف": ChatPrivileges(can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_change_info=True, can_invite_users=True, can_pin_messages=True),
    "ادمن": ChatPrivileges(can_delete_messages=True, can_restrict_members=True, can_invite_users=True, can_pin_messages=True),
    "مميز": ChatPrivileges(can_delete_messages=True, can_restrict_members=True),
}

@Client.on_message(filters.group & filters.command(["رفع", "promote"]))
async def promote_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: /رفع [الرتبة]\nالرتب: مالك، مشرف، ادمن، مميز")
    rank = message.command[1]
    if rank not in RANKS:
        return await message.reply(f"❌ الرتب ماشي موجودة\n{'، '.join(RANKS.keys())}")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.promote_chat_member(message.chat.id, target.id, privileges=RANKS[rank])
        await message.reply(f"👑 تم رفع {target.mention} {rank}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["تنزيل", "demote"]))
async def demote_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.promote_chat_member(message.chat.id, target.id, privileges=ChatPrivileges())
        await message.reply(f"⬇️ تم تنزيل {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["مسح", "purge"]))
async def purge_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    if not message.reply_to_message:
        return await message.reply("❌ رد على الرسالة اللي تحب تمسح منها")
    try:
        msgs = [message.id, message.reply_to_message.id]
        async for m in client.get_chat_history(message.chat.id, limit=100, offset_id=message.reply_to_message.id):
            msgs.append(m.id)
        await client.delete_messages(message.chat.id, msgs)
        await message.reply(f"🗑 تم مسح {len(msgs)} رسالة")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["طرد", "kick"]))
async def kick_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await client.unban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 تم طرد {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["حظر", "ban"]))
async def ban_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 تم حظر {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["كتم", "mute"]))
async def mute_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    target = await get_target(client, message)
    if not target:
        return await message.reply("❌ رد على رسالة العضو")
    try:
        await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions(can_send_messages=False))
        await message.reply(f"🔇 تم كتم {target.mention}")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.group & filters.command(["تفعيل", "enable"]))
async def enable_bot(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    from database import add_group, update_group
    await add_group(message.chat.id, message.chat.title)
    await update_group(message.chat.id, "protection", True)
    await message.reply("✅ تم تفعيل البوت")

@Client.on_message(filters.group & filters.command(["تعطيل", "disable"]))
async def disable_bot(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ هاد الأمر خاص بالمشرفين")
    from database import update_group
    await update_group(message.chat.id, "protection", False)
    await message.reply("❌ تم تعطيل البوت")
