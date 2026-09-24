import random
from pyrogram import Client, filters
from pyrogram.types import Message

SURAHS = {
    "الفاتحة": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\nالْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\nالرَّحْمَٰنِ الرَّحِيمِ\nمَالِكِ يَوْمِ الدِّينِ\nإِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ\nاهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ\nصِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
    "الإخلاص": "قُلْ هُوَ اللَّهُ أَحَدٌ\nاللَّهُ الصَّمَدُ\nلَمْ يَلِدْ وَلَمْ يُولَدْ\nوَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
    "الفلق": "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ\nمِن شَرِّ مَا خَلَقَ\nوَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ\nوَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ\nوَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ",
    "الناس": "قُلْ أَعُوذُ بِرَبِّ النَّاسِ\nمَلِكِ النَّاسِ\nإِلَٰهِ النَّاسِ\nمِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ\nالَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ\nمِنَ الْجِنَّةِ وَالنَّاسِ",
    "الكوثر": "إِنَّا أَعْطَيْنَاكَ الْكَوْثَرَ\nفَصَلِّ لِرَبِّكَ وَانْحَرْ\nإِنَّ شَانِئَكَ هُوَ الْأَبْتَرُ",
    "العصر": "وَالْعَصْرِ\nإِنَّ الْإِنسَانَ لَفِي خُسْرٍ\nإِلَّا الَّذِينَ آمَنُوا وَعَمِلُوا الصَّالِحَاتِ وَتَوَاصَوْا بِالْحَقِّ وَتَوَاصَوْا بِالصَّبْرِ",
}

AZKAR = [
    "سبحان الله وبحمده، سبحان الله العظيم 🌿",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير 🌿",
    "اللهم صل وسلم على نبينا محمد 🌿",
    "أستغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه 🌿",
    "لا حول ولا قوة إلا بالله 🌿",
    "سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر 🌿",
    "اللهم أجرني من النار 🌿",
    "اللهم إني أسألك الجنة وأعوذ بك من النار 🌿",
    "حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم 🌿",
    "اللهم اغفر لي ولوالدي وللمؤمنين يوم يقوم الحساب 🌿",
]

POEMS = [
    "إذا الشعبُ يوماً أرادَ الحياةَ\nفلا بُدَّ أن يستجيبَ القدرْ 🌿",
    "وما نيلُ المطالبِ بالتمني\nولكن تُؤخذُ الدنيا غِلابا 🌿",
    "قم للمعلمِ وفِّهِ التبجيلا\nكادَ المعلمُ أن يكونَ رسولا 🌿",
    "أنا الذي نظرَ الأعمى إلى أدبي\nوأسْمعتْ كلماتي مَن به صَمَمُ 🌿",
    "لا تحسبِ المجدَ تمراً أنت آكلُهُ\nلن تبلغَ المجدَ حتى تلعقَ الصبرا 🌿",
    "ولستُ أرى السعادةَ جمعَ مالٍ\nولكنَّ التقيَّ هو السعيدُ 🌿",
    "ومن يتهيبْ صعودَ الجبالِ\nيعشْ أبدَ الدهرِ بين الحفرْ 🌿",
]

QUOTES = [
    "«من جدّ وجد، ومن زرع حصد» 🌟",
    "«لا تحزن إن الله معنا» 🌟",
    "«النجاح ليس نهاية، والفشل ليس قاتلاً» 🌟",
    "«كن جميلاً ترى الوجود جميلاً» 🌟",
    "«الحياة قصيرة، فلا تضيعها في الندم» 🌟",
    "«العلم نور والجهل ظلام» 🌟",
    "«الصبر مفتاح الفرج» 🌟",
    "«من سار على الدرب وصل» 🌟",
]

STORIES = [
    "📖 **قصة الأرنب والسلحفاة**\n\nكان الأرنب يفتخر بسرعته، والسلحفاة بطيئة لكن مثابرة. في السباق، نام الأرنب، وفازت السلحفاة. العبرة: المثابرة تغلب الغرور.",
    "📖 **قصة الأسد والفأر**\n\nأوقع الأسد فأراً صغيراً، فاستعطفه الفأر. في يوم، وقع الأسد في شبكة، فجاء الفأر وقرض الشبكة وأنقذه. العبرة: لا تحتقر أحداً.",
    "📖 **قصة الغراب والعطش**\n\nكان الغراب عطشاناً، فوجد جرة فيها ماء قليل. وضع الحصى فيها حتى ارتفع الماء وشرب. العبرة: الحكمة والصبر.",
    "📖 **قصة النملة والجندب**\n\nفي الصيف، جمعت النملة الطعام، ولعب الجندب. في الشتاء، جاع الجندب، فساعدته النملة. العبرة: الاستعداد للغد.",
]

HYDRAS = ["✨ 𝐒𝐎𝐒𝐎 ✨", "🌟 𝐑𝐀𝐇𝐀 🌟", "💫 𝐁𝐎𝐓 💫", "🔥 𝐒𝐎𝐒𝐎 𝐁𝐎𝐓 🔥", "⚡ 𝐏𝐑𝐎 ⚡", "👑 𝐊𝐈𝐍𝐆 👑", "💎 𝐃𝐈𝐀𝐌𝐎𝐍𝐃 💎"]

@Client.on_message(filters.group & filters.command(["قران", "quran"]))
async def quran_cmd(client, message: Message):
    if len(message.command) < 2:
        text = "📖 **السور المتوفرة:**\n\n" + "\n".join(f"• {s}" for s in SURAHS.keys())
        return await message.reply(text + "\n\nاكتب: `/قران [اسم السورة]`")
    name = message.text.split(None, 1)[1]
    if name not in SURAHS:
        return await message.reply(f"❌ السورة ماشي موجودة\nالسور: {'، '.join(SURAHS.keys())}")
    await message.reply(f"📖 **سورة {name}**\n\n{SURAHS[name]}")

@Client.on_message(filters.group & filters.command(["اذكار", "azkar"]))
async def azkar_cmd(client, message: Message):
    await message.reply(f"🤲 **ذكر:**\n\n{random.choice(AZKAR)}")

@Client.on_message(filters.group & filters.command(["شعر", "poetry"]))
async def poetry_cmd(client, message: Message):
    await message.reply(f"📜 **بيت شعر:**\n\n{random.choice(POEMS)}")

@Client.on_message(filters.group & filters.command(["اقتباسات", "quotes"]))
async def quotes_cmd(client, message: Message):
    await message.reply(f"💬 **اقتباس:**\n\n{random.choice(QUOTES)}")

@Client.on_message(filters.group & filters.command(["قصص", "stories"]))
async def stories_cmd(client, message: Message):
    await message.reply(random.choice(STORIES))

@Client.on_message(filters.group & filters.command(["هيدرات", "hydras"]))
async def hydras_cmd(client, message: Message):
    await message.reply(f"🎭 **هيدر:**\n\n{random.choice(HYDRAS)}")

@Client.on_message(filters.group & filters.command(["اطريني", "atrini"]))
async def atrini_cmd(client, message: Message):
    await message.reply("🎵 اكتب اسم الأغنية اللي تحب تسمعها")

@Client.on_message(filters.group & filters.command(["اغاني", "songs"]))
async def songs_cmd(client, message: Message):
    await message.reply("🎶 قائمة الأغاني متوفرة قريباً")

@Client.on_message(filters.group & filters.command(["تريد", "traid"]))
async def traid_cmd(client, message: Message):
    await message.reply("🔄 قسم التريد - قريباً")

@Client.on_message(filters.group & filters.command(["كتب", "books"]))
async def books_cmd(client, message: Message):
    await message.reply("📚 قسم الكتب - قريباً")

@Client.on_message(filters.group & filters.command(["افلام", "movies"]))
async def movies_cmd(client, message: Message):
    await message.reply("🎬 قسم الأفلام - قريباً")

@Client.on_message(filters.group & filters.command(["جداريات", "walls"]))
async def walls_cmd(client, message: Message):
    await message.reply("🖼 قسم الجداريات - قريباً")

@Client.on_message(filters.group & filters.command(["مميز", "vip"]))
async def vip_cmd(client, message: Message):
    await message.reply("⭐ قسم المميزين - قريباً")

@Client.on_message(filters.group & filters.command(["ايدت", "edit"]))
async def edit_cmd(client, message: Message):
    await message.reply("🎨 قسم الإيدت - قريباً")

@Client.on_message(filters.group & filters.command(["قيفات", "gifts"]))
async def gifts_cmd(client, message: Message):
    await message.reply("🎁 قسم القيفات - قريباً")

@Client.on_message(filters.group & filters.command(["افارات", "avatars"]))
async def avatars_cmd(client, message: Message):
    await message.reply("🖼 قسم الافتارات - قريباً")

@Client.on_message(filters.group & filters.command(["تطقيم", "taqteem"]))
async def taqteem_cmd(client, message: Message):
    await message.reply("🎭 قسم التطقيم - قريباً")
