from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import add_user

WELCOME_TEXT = """╭━━〔  𝐒𝐎𝐒𝐎  〕━━╮
┃
┃ ◈ أهلاً بك عزيزي في بوت 𝐒𝐎𝐒𝐎
┃ ◈ اختصاصي حماية المجموعات وتسليه الاعضاء
┃ ◈ سرعة ، آمان ، حماية ، تسليه ، افتارات
┃ ◈ البوت خالي من الاعلانات المزعجة
┃ ◈ ارفعني مشرف واكتب تفعيل 🍷
┃
┃ ◈ مطور البوت ← @xnwam
┃ ◈ قناة التحديثات ← @Soso_vor
┃
╰━━〔  𝐒𝐎𝐒𝐎  〕━━╯"""

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1️⃣ أوامر الادمنية", callback_data="menu_admin"), InlineKeyboardButton("2️⃣ أوامر الاعدادات", callback_data="menu_settings")],
        [InlineKeyboardButton("3️⃣ القفل والفتح", callback_data="menu_locks"), InlineKeyboardButton("4️⃣ التسلية", callback_data="menu_fun")],
        [InlineKeyboardButton("5️⃣ Dev", callback_data="menu_dev"), InlineKeyboardButton("6️⃣ الخدمية", callback_data="menu_service")],
        [InlineKeyboardButton("🟢 التفعيل والتعطيل", callback_data="menu_toggle"), InlineKeyboardButton("🔵 القفل والفتح", callback_data="menu_lock_unlock")],
        [InlineKeyboardButton("🚀 Source SOSO", url="https://t.me/Soso_vor")],
        [InlineKeyboardButton("❌ اخفاء الامر", callback_data="hide_menu")],
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 رفع", callback_data="adm_promote"), InlineKeyboardButton("⬇️ تنزيل", callback_data="adm_demote")],
        [InlineKeyboardButton("🗑 مسح", callback_data="adm_purge"), InlineKeyboardButton("🚫 طرد وحظر", callback_data="adm_ban")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="menu_main")],
    ])

def settings_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 الرابط", callback_data="set_link"), InlineKeyboardButton("📋 القوانين", callback_data="set_rules")],
        [InlineKeyboardButton("👥 المالكين", callback_data="set_owners"), InlineKeyboardButton("🛡 الادمنيه", callback_data="set_admins")],
        [InlineKeyboardButton("📊 معلوماتي", callback_data="set_info"), InlineKeyboardButton("⚙️ المجموعه", callback_data="set_group")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="menu_main")],
    ])

def locks_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 الروابط", callback_data="lock_links"), InlineKeyboardButton("🖼 الكلايش", callback_data="lock_stickers")],
        [InlineKeyboardButton("⌨️ الكيبورد", callback_data="lock_keyboard"), InlineKeyboardButton("🎵 الاغاني", callback_data="lock_songs")],
        [InlineKeyboardButton("🎬 المتحركه", callback_data="lock_gifs"), InlineKeyboardButton("📁 الملفات", callback_data="lock_files")],
        [InlineKeyboardButton("💬 الدردشه", callback_data="lock_chat"), InlineKeyboardButton("📹 الفيديو", callback_data="lock_video")],
        [InlineKeyboardButton("📷 الصور", callback_data="lock_photos"), InlineKeyboardButton("👤 المعرفات", callback_data="lock_usernames")],
        [InlineKeyboardButton("📢 التاك", callback_data="lock_mention"), InlineKeyboardButton("🤖 البوتات", callback_data="lock_bots")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu_main"), InlineKeyboardButton("❌ اخفاء", callback_data="hide_menu")],
    ])

def fun_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💕 نسبه الحب", callback_data="fun_love"), InlineKeyboardButton("🤪 نسبه الغباء", callback_data="fun_stupid")],
        [InlineKeyboardButton("💑 زواج", callback_data="fun_marry"), InlineKeyboardButton("💔 طلاق", callback_data="fun_divorce")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="menu_main")],
    ])

def dev_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اذاعة", callback_data="dev_broadcast"), InlineKeyboardButton("📊 احصائيات", callback_data="dev_stats")],
        [InlineKeyboardButton("🔄 اعادة تشغيل", callback_data="dev_restart"), InlineKeyboardButton("🛑 ايقاف", callback_data="dev_shutdown")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="menu_main")],
    ])

def service_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 قران", callback_data="srv_quran"), InlineKeyboardButton("🤲 اذكار", callback_data="srv_azkar")],
        [InlineKeyboardButton("📜 شعر", callback_data="srv_poetry"), InlineKeyboardButton("💬 اقتباسات", callback_data="srv_quotes")],
        [InlineKeyboardButton("🎵 اطريني", callback_data="srv_atrini"), InlineKeyboardButton("🎶 اغاني", callback_data="srv_songs")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="menu_main")],
    ])

def toggle_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 تفعيل الرابط", callback_data="tog_link_on"), InlineKeyboardButton("🚫 تعطيل الرابط", callback_data="tog_link_off")],
        [InlineKeyboardButton("👋 تفعيل الترحيب", callback_data="tog_welcome_on"), InlineKeyboardButton("🚫 تعطيل الترحيب", callback_data="tog_welcome_off")],
        [InlineKeyboardButton("💬 تفعيل الردود", callback_data="tog_reply_on"), InlineKeyboardButton("🚫 تعطيل الردود", callback_data="tog_reply_off")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu_main"), InlineKeyboardButton("❌ اخفاء", callback_data="hide_menu")],
    ])

def lock_unlock_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 قفل الكل", callback_data="lockall"), InlineKeyboardButton("🔓 فتح الكل", callback_data="unlockall")],
        [InlineKeyboardButton("🔗 قفل الروابط", callback_data="lock_links"), InlineKeyboardButton("🔗 فتح الروابط", callback_data="unlock_links")],
        [InlineKeyboardButton("🖼 قفل الصور", callback_data="lock_photos"), InlineKeyboardButton("🖼 فتح الصور", callback_data="unlock_photos")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu_main"), InlineKeyboardButton("❌ اخفاء", callback_data="hide_menu")],
    ])

@Client.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message: Message):
    user = message.from_user
    await add_user(user.id, user.first_name, user.username)
    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu(),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^menu_"))
async def menu_callback(client, query: CallbackQuery):
    data = query.data
    if data == "menu_main":
        await query.message.edit_text(WELCOME_TEXT, reply_markup=main_menu(), disable_web_page_preview=True)
    elif data == "menu_admin":
        await query.message.edit_text("👑 أوامر الادمنية\n\nاختر:", reply_markup=admin_menu())
    elif data == "menu_settings":
        await query.message.edit_text("⚙️ أوامر الاعدادات\n\nاختر:", reply_markup=settings_menu())
    elif data == "menu_locks":
        await query.message.edit_text("🔒 القفل والفتح\n\nاختر:", reply_markup=locks_menu())
    elif data == "menu_fun":
        await query.message.edit_text("🎮 التسلية\n\nاختر:", reply_markup=fun_menu())
    elif data == "menu_dev":
        await query.message.edit_text("🛠 Dev\n\nاختر:", reply_markup=dev_menu())
    elif data == "menu_service":
        await query.message.edit_text("🛎 الخدمية\n\nاختر:", reply_markup=service_menu())
    elif data == "menu_toggle":
        await query.message.edit_text("🔘 التفعيل والتعطيل\n\nاختر:", reply_markup=toggle_menu())
    elif data == "menu_lock_unlock":
        await query.message.edit_text("🔐 القفل والفتح\n\nاختر:", reply_markup=lock_unlock_menu())
    elif data == "hide_menu":
        await query.message.delete()
    else:
        await query.answer("⏳ هاد القسم مزال", show_alert=True)
