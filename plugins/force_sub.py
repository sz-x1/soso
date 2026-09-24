from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from config import Config
from database import force_channels_col, db

async def get_force_channels():
    channels = []
    async for ch in force_channels_col.find({}):
        channels.append({
            "id": ch["channel_id"],
            "title": ch["title"],
            "link": ch["link"]
        })
    return channels

async def add_force_channel(channel_id, title, link):
    if not await force_channels_col.find_one({"channel_id": channel_id}):
        await force_channels_col.insert_one({
            "channel_id": channel_id,
            "title": title,
            "link": link
        })
        return True
    return False

async def remove_force_channel(channel_id):
    result = await force_channels_col.delete_one({"channel_id": channel_id})
    return result.deleted_count > 0

force_sub_status_col = db["force_sub_status"]

async def is_force_sub_enabled():
    doc = await force_sub_status_col.find_one({"_id": "status"})
    return doc.get("enabled", True) if doc else True

async def set_force_sub_enabled(enabled: bool):
    await force_sub_status_col.update_one(
        {"_id": "status"},
        {"$set": {"enabled": enabled}},
        upsert=True
    )

async def is_subscribed(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(channel_id, user_id)
        return member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]
    except UserNotParticipant:
        return False
    except Exception:
        return False

async def check_all_subscriptions(client, user_id, channels):
    not_subscribed = []
    for ch in channels:
        if not await is_subscribed(client, user_id, ch["id"]):
            not_subscribed.append(ch)
    return not_subscribed

def build_sub_message(not_subscribed):
    text = "🔒 **الاشتراك الإجباري**\n\nعزيزي، باش تستعمل البوت خاصك تكون مشترك فالقنوات التالية:\n\n"
    buttons = []
    for ch in not_subscribed:
        text += f"• [{ch['title']}]({ch['link']})\n"
        buttons.append([InlineKeyboardButton(f"📢 {ch['title']}", url=ch["link"])])
    text += "\nبعد ما تشترك، اضغط على **✅ تحقق**"
    buttons.append([InlineKeyboardButton("✅ تحقق", callback_data="check_sub")])
    return text, InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex("^check_sub$"))
async def check_sub_callback(client, query: CallbackQuery):
    from plugins.start import WELCOME_TEXT, main_menu
    user_id = query.from_user.id
    channels = await get_force_channels()
    if not channels:
        return await query.answer("✅ ما كاينش اشتراك إجباري", show_alert=True)
    not_subscribed = await check_all_subscriptions(client, user_id, channels)
    if not_subscribed:
        text = "❌ **مزال ما اشتركتش فـ:**\n\n"
        for ch in not_subscribed:
            text += f"• {ch['title']}\n"
        return await query.answer(text, show_alert=True)
    await query.answer("✅ تم التحقق!", show_alert=False)
    await query.message.delete()
    await query.message.reply_text(WELCOME_TEXT, reply_markup=main_menu(), disable_web_page_preview=True)

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["اضف قناة", "addchannel"]))
async def add_channel_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/اضف قناة [ID القناة]`\n\nمثال: `/اضف قناة -1001234567890`\n\n⚠️ خاص البوت يكون مشرف فالقناة")
    try:
        channel_id = int(message.command[1])
    except:
        return await message.reply("❌ ID القناة خاصو يكون رقم")
    try:
        chat = await client.get_chat(channel_id)
        title = chat.title
        username = chat.username
        if username:
            link = f"https://t.me/{username}"
        else:
            try:
                invite = await client.create_chat_invite_link(channel_id)
                link = invite.invite_link
            except:
                return await message.reply("❌ ما قدرتش نجيب رابط القناة")
        added = await add_force_channel(channel_id, title, link)
        if added:
            await message.reply(f"✅ **تمت إضافة القناة:**\n\n• {title}\n• {link}")
        else:
            await message.reply("❌ القناة موجودة من قبل")
    except Exception as e:
        await message.reply(f"❌ خطأ: {e}")

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["حذف قناة", "delchannel"]))
async def del_channel_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/حذف قناة [ID القناة]`")
    try:
        channel_id = int(message.command[1])
    except:
        return await message.reply("❌ ID القناة خاصو يكون رقم")
    removed = await remove_force_channel(channel_id)
    if removed:
        await message.reply("✅ **تم حذف القناة**")
    else:
        await message.reply("❌ القناة ماشي موجودة")

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["القنوات", "channels"]))
async def list_channels_cmd(client, message: Message):
    channels = await get_force_channels()
    if not channels:
        return await message.reply("📝 **ما كاين حتى قناة مضافة**")
    text = "📢 **القنوات المضافة:**\n\n"
    for i, ch in enumerate(channels, 1):
        text += f"{i}. **{ch['title']}**\n   ID: `{ch['id']}`\n   [رابط]({ch['link']})\n\n"
    await message.reply(text, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["تفعيل الاشتراك", "forcesub on"]))
async def enable_force_sub(client, message: Message):
    await set_force_sub_enabled(True)
    await message.reply("✅ **تم تفعيل الاشتراك الإجباري**")

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command(["تعطيل الاشتراك", "forcesub off"]))
async def disable_force_sub(client, message: Message):
    await set_force_sub_enabled(False)
    await message.reply("❌ **تم تعطيل الاشتراك الإجباري**")
