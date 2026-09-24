import random
from pyrogram import Client, filters
from pyrogram.types import Message

def get_target(client, message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None

@Client.on_message(filters.group & filters.command(["نسبه الحب", "love"]))
async def love_percent(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    p = random.randint(1, 100)
    bar = "❤️" * (p // 10) + "🖤" * (10 - p // 10)
    await message.reply(f"💕 نسبة الحب\n\n• {message.from_user.mention} ❤️ {t.mention}\n• {bar}\n• {p}%")

@Client.on_message(filters.group & filters.command(["نسبه الغباء", "stupid"]))
async def stupid_percent(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"🤪 نسبة الغباء\n\n• {t.mention}: {random.randint(1,100)}%")

@Client.on_message(filters.group & filters.command(["زواج", "marry"]))
async def marry(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"💍 مبروك!\n• {message.from_user.mention} 💑 {t.mention}")

@Client.on_message(filters.group & filters.command(["طلاق", "divorce"]))
async def divorce(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"💔 تم الطلاق!\n• {message.from_user.mention} 💔 {t.mention}")

@Client.on_message(filters.group & filters.command(["تتزوجني", "propose"]))
async def propose(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    ans = random.choice(["💍 إيه نوافق", "💔 لا ما نوافقش", "🤔 خلي نفكر"])
    await message.reply(f"💌 {message.from_user.mention} طلب الزواج من {t.mention}\n\n{ans}")

@Client.on_message(filters.group & filters.command(["شيهي", "shihi"]))
async def shihi(client, message: Message):
    await message.reply(f"🍽 شيهي {message.from_user.mention} صحه وراحه 🍕")

@Client.on_message(filters.group & filters.command(["صيح", "scream"]))
async def scream(client, message: Message):
    await message.reply(f"📢 صيحة من {message.from_user.mention}")

@Client.on_message(filters.group & filters.command(["اهديه", "gift"]))
async def gift(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"🎁 {message.from_user.mention} أهدى {t.mention} {random.choice(['🌹','🎁','💐','🧸','💍','🍫'])}")

@Client.on_message(filters.group & filters.command(["البايو", "bio"]))
async def bio(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"📝 بايو {t.mention}:\n\n{random.choice(['محب للسلام ✌️','طموح 🔥','بسيط 😌','مجتهد 💪','رومانسي 🌹'])}")

@Client.on_message(filters.group & filters.command(["افتاره", "avatar"]))
async def avatar(client, message: Message):
    t = get_target(client, message)
    if not t:
        return await message.reply("❌ رد على رسالة العضو")
    await message.reply(f"🖼 افتار {t.mention}: {random.choice(['🐱','🦁','🐺','🦊','🐼','🐸','🐧','🦅'])}")

@Client.on_message(filters.group & filters.command(["معنى", "meaning"]))
async def meaning(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: /معنى اسمك")
    name = message.text.split(None, 1)[1]
    await message.reply(f"📖 معنى {name}: {random.choice(['القوي','الجميل','الشجاع','الحكيم','الكريم','النور','الصفا'])}")

@Client.on_message(filters.group & filters.command(["العمر", "age"]))
async def age(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: /العمر 20")
    await message.reply(f"🎂 عمرك: {message.command[1]} سنة")

@Client.on_message(filters.group & filters.command(["زخرف", "decorate"]))
async def decorate(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: /زخرف اسمك")
    n = message.text.split(None, 1)[1]
    await message.reply(f"✨ {n} ✨\n✿ {n} ✿\n❥ {n} ❥\n★彡 {n} 彡★")

@Client.on_message(filters.group & filters.command(["قوقل", "google"]))
async def google_search(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: /قوقل كلام البحث")
    q = message.text.split(None, 1)[1]
    await message.reply(f"🔍 نتائج:\nhttps://www.google.com/search?q={q.replace(' ','+')}")
