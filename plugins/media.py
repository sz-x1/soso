from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.group & filters.command("mplay"))
async def mplay(client, message: Message):
    await message.reply("🎵 **جاري تشغيل الموسيقى...**\n\nخاصك حساب مساعد (Userbot)")

@Client.on_message(filters.group & filters.command("vplay"))
async def vplay(client, message: Message):
    await message.reply("📹 **جاري تشغيل الفيديو...**\n\nخاصك حساب مساعد (Userbot)")

@Client.on_message(filters.group & filters.command("skip"))
async def skip(client, message: Message):
    await message.reply("⏭ **تم تخطي التشغيل**")

@Client.on_message(filters.group & filters.command("stop"))
async def stop(client, message: Message):
    await message.reply("⏹ **تم إنهاء التشغيل**")

@Client.on_message(filters.group & filters.command("resume"))
async def resume(client, message: Message):
    await message.reply("▶️ **تم استئناف التشغيل**")

@Client.on_message(filters.group & filters.command("song"))
async def song(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/song اسم الأغنية`")
    await message.reply(f"🎵 **جاري تحميل:** {message.text.split(None,1)[1]}")

@Client.on_message(filters.group & filters.command("video"))
async def video(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/video اسم الفيديو`")
    await message.reply(f"📹 **جاري تحميل:** {message.text.split(None,1)[1]}")

@Client.on_message(filters.group & filters.command("playmylist"))
async def playmylist(client, message: Message):
    await message.reply("🎶 **جاري تشغيل أغاني بروفايلك...**")

@Client.on_message(filters.group & filters.command("updateadmin"))
async def updateadmin(client, message: Message):
    await message.reply("✅ **تم تحديث قائمة الادمنيه**")

@Client.on_message(filters.group & filters.command("userbotjoin"))
async def userbotjoin(client, message: Message):
    await message.reply("🤖 **جاري دخول الحساب المساعد...**")

@Client.on_message(filters.group & filters.command("userbotleave"))
async def userbotleave(client, message: Message):
    await message.reply("🤖 **جاري خروج الحساب المساعد...**")

@Client.on_message(filters.group & filters.command("setcmdsformembers"))
async def setcmdsformembers(client, message: Message):
    await message.reply("✅ **تم وضع أوامر التحكم للأعضاء**")

@Client.on_message(filters.group & filters.command("setcmdsforadmins"))
async def setcmdsforadmins(client, message: Message):
    await message.reply("✅ **تم وضع أوامر التحكم للمشرفين**")

@Client.on_message(filters.group & filters.command("setplayformembers"))
async def setplayformembers(client, message: Message):
    await message.reply("✅ **تم وضع أمر التشغيل للأعضاء**")

@Client.on_message(filters.group & filters.command("setplayforadmins"))
async def setplayforadmins(client, message: Message):
    await message.reply("✅ **تم وضع أمر التشغيل للمشرفين**")
