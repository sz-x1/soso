from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from database import whispers_col

async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@Client.on_message(filters.group & filters.command(["همس", "whisper"]))
async def whisper_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ رد على رسالة العضو واكتب /همس النص")
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        return await message.reply("❌ ما تقدرش تهمس لنفسك")
    if len(message.command) < 2:
        return await message.reply("❌ اكتب النص بعد /همس")
    text = message.text.split(None, 1)[1]
    whisper_id = f"{message.chat.id}_{message.id}"
    await whispers_col.insert_one({
        "whisper_id": whisper_id,
        "chat_id": message.chat.id,
        "from_id": message.from_user.id,
        "from_name": message.from_user.first_name,
        "to_id": target.id,
        "to_name": target.first_name,
        "text": text,
        "paid_viewers": []
    })
    buttons = [
        [InlineKeyboardButton("📩 شوف الهمسة", callback_data=f"view_{whisper_id}")],
        [InlineKeyboardButton("💎 شوفها بـ 10 نجوم", callback_data=f"pay_{whisper_id}")],
    ]
    await message.reply(
        f"🤫 **همسة من** {message.from_user.mention} **إلى** {target.mention}\n\n"
        f"• الهمسة يشوفها غير {target.mention} والمشرفين\n"
        f"• أي واحد آخر يقدر يشوفها بـ 10 نجوم ⭐",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    try:
        await message.delete()
    except:
        pass

@Client.on_callback_query(filters.regex("^view_"))
async def view_whisper(client, query: CallbackQuery):
    wid = query.data.replace("view_", "")
    w = await whispers_col.find_one({"whisper_id": wid})
    if not w:
        return await query.answer("❌ الهمسة ماشي موجودة", show_alert=True)
    uid = query.from_user.id
    can = False
    if uid in [w["from_id"], w["to_id"]] or uid in w.get("paid_viewers", []):
        can = True
    elif await is_admin(client, w["chat_id"], uid):
        can = True
    if not can:
        return await query.answer("🔒 هاد الهمسة ماشي ليك\nتقدر تشوفها بـ 10 نجوم ⭐", show_alert=True)
    await query.answer(f"🤫 الهمسة:\n\n{w['text']}", show_alert=True)

@Client.on_callback_query(filters.regex("^pay_"))
async def pay_whisper(client, query: CallbackQuery):
    wid = query.data.replace("pay_", "")
    w = await whispers_col.find_one({"whisper_id": wid})
    if not w:
        return await query.answer("❌ الهمسة ماشي موجودة", show_alert=True)
    uid = query.from_user.id
    if uid in w.get("paid_viewers", []):
        return await query.answer("✅ راك خلصت من قبل", show_alert=True)
    if uid in [w["from_id"], w["to_id"]]:
        return await query.answer("✅ هاد الهمسة ليك", show_alert=True)
    await query.answer("💎 خاصك تدفع 10 نجوم فـ الخاص", show_alert=True)
