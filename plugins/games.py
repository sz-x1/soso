import random
from pyrogram import Client, filters
from pyrogram.types import Message

active_games = {}

# ============================================================
# 🎯 تخمين الرقم
# ============================================================

@Client.on_message(filters.group & filters.command(["تخمين", "guess"]))
async def guess_game(client, message: Message):
    if message.chat.id in active_games:
        return await message.reply("⚠️ كاين لعبة شغالة دابا")
    number = random.randint(1, 100)
    active_games[message.chat.id] = number
    await message.reply("🎮 **لعبة تخمين الرقم**\n\nخمنت رقم بين 1 و 100\nاكتب `/رقمي [الرقم]`")

@Client.on_message(filters.group & filters.command(["رقمي", "mynum"]))
async def guess_answer(client, message: Message):
    if message.chat.id not in active_games:
        return await message.reply("❌ ما كاينش لعبة شغالة")
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/رقمي 50`")
    try:
        guess = int(message.command[1])
    except:
        return await message.reply("❌ اكتب رقم")
    number = active_games[message.chat.id]
    if guess == number:
        del active_games[message.chat.id]
        await message.reply(f"🎉 مبروك! {message.from_user.mention} خمن الرقم {number}")
    elif guess < number:
        await message.reply("📉 الرقم أكبر")
    else:
        await message.reply("📈 الرقم أصغر")

# ============================================================
# 🏆 XO - إكس أو
# ============================================================

XO_EMPTY = "⬜"
XO_X = "❌"
XO_O = "⭕"

xo_games = {}

def xo_check_winner(board):
    lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for a, b, c in lines:
        if board[a] != XO_EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None

def xo_board_markup(chat_id, board):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    btns = []
    for i in range(9):
        if board[i] == XO_EMPTY:
            btns.append(InlineKeyboardButton(XO_EMPTY, callback_data=f"xo_pick_{chat_id}_{i}"))
        else:
            btns.append(InlineKeyboardButton(board[i], callback_data=f"xo_no_{chat_id}"))
    return InlineKeyboardMarkup([btns[0:3], btns[3:6], btns[6:9]])

@Client.on_message(filters.group & filters.command(["xo", "اكس"]))
async def xo_start(client, message: Message):
    chat_id = message.chat.id
    if chat_id in xo_games:
        return await message.reply("⚠️ كاين لعبة XO شغالة")
    xo_games[chat_id] = {
        "board": [XO_EMPTY] * 9,
        "players": {},
        "turn": None,
        "scores": {"X": 0, "O": 0},
        "round": 1,
    }
    await message.reply("🏆 **XO**\n\n✅ كتب `/انضم` باش تشارك\n⚠️ خاصك لاعبين")

@Client.on_message(filters.group & filters.command(["انضم", "join"]))
async def xo_join(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in xo_games:
        return await message.reply("❌ ما كاينش لعبة، اكتب `/xo`")
    g = xo_games[chat_id]
    uid = message.from_user.id
    if uid in g["players"]:
        return await message.reply("❌ راك منضم")
    if len(g["players"]) >= 2:
        return await message.reply("❌ اللاعبين كاملين")
    g["players"][uid] = message.from_user.first_name
    await message.reply(f"✅ {message.from_user.mention} انضم\n👥 اللاعبين: {len(g['players'])}/2")
    if len(g["players"]) == 2:
        players = list(g["players"].keys())
        random.shuffle(players)
        g["xo_players"] = {"X": players[0], "O": players[1]}
        g["turn"] = players[0]
        await message.reply(
            f"🏆 **XO تبدا!**\n\n"
            f"❌ {g['players'][players[0]]}\n"
            f"⭕ {g['players'][players[1]]}\n\n"
            f"🎯 دور: {g['players'][players[0]]}"
        )
        sent = await message.reply(
            f"🎮 دور {g['players'][g['turn']]}",
            reply_markup=xo_board_markup(chat_id, g["board"])
        )
        g["last_board_id"] = sent.id

@Client.on_callback_query(filters.regex("^xo_"))
async def xo_callback(client, query):
    if query.data.startswith("xo_no_"):
        return await query.answer("❌ مشغول")
    parts = query.data.split("_")
    chat_id = int(parts[2])
    pos = int(parts[3])
    uid = query.from_user.id
    if chat_id not in xo_games:
        return await query.answer("❌")
    g = xo_games[chat_id]
    if uid not in g["players"]:
        return await query.answer("❌ ماشي لاعب", show_alert=True)
    if uid != g["turn"]:
        return await query.answer("⏰ ماشي دورك!", show_alert=True)
    if g["board"][pos] != XO_EMPTY:
        return await query.answer("❌ مشغول")
    sym = XO_X if uid == g["xo_players"]["X"] else XO_O
    g["board"][pos] = sym
    await query.answer(f"✅ {sym}")
    winner = xo_check_winner(g["board"])
    if winner:
        if winner == XO_X:
            g["scores"]["X"] += 1
            wuid = g["xo_players"]["X"]
        else:
            g["scores"]["O"] += 1
            wuid = g["xo_players"]["O"]
        await client.send_message(chat_id, f"🎉 {g['players'][wuid]} فاز!\n📊 ❌ {g['scores']['X']} — {g['scores']['O']} ⭕")
        if g["scores"]["X"] >= 3 or g["scores"]["O"] >= 3:
            await client.send_message(chat_id, f"🏆 الفائز النهائي: {g['players'][wuid]}! 🎁 +10")
            del xo_games[chat_id]
            return
        g["round"] += 1
        g["board"] = [XO_EMPTY] * 9
        g["turn"] = g["xo_players"]["X"]
        sent = await client.send_message(
            chat_id,
            f"🎮 جولة جديدة ({g['round']}) — دور {g['players'][g['turn']]}",
            reply_markup=xo_board_markup(chat_id, g["board"])
        )
        g["last_board_id"] = sent.id
        return
    if XO_EMPTY not in g["board"]:
        await client.send_message(chat_id, "🤝 تعادل!")
        g["board"] = [XO_EMPTY] * 9
        g["turn"] = g["xo_players"]["X"]
        sent = await client.send_message(
            chat_id,
            f"🎮 جولة جديدة — دور {g['players'][g['turn']]}",
            reply_markup=xo_board_markup(chat_id, g["board"])
        )
        g["last_board_id"] = sent.id
        return
    g["turn"] = g["xo_players"]["O"] if uid == g["xo_players"]["X"] else g["xo_players"]["X"]
    try:
        await client.edit_message_reply_markup(chat_id, g["last_board_id"], reply_markup=xo_board_markup(chat_id, g["board"]))
    except:
        sent = await client.send_message(
            chat_id,
            f"🎮 دور {g['players'][g['turn']]}",
            reply_markup=xo_board_markup(chat_id, g["board"])
        )
        g["last_board_id"] = sent.id

# ============================================================
# 🧩 الذاكرة
# ============================================================

MEMORY_EMOJIS = ["🍎", "🍌", "🍇", "🍓", "🍒", "🍉", "🥝", "🍑"]
memory_games = {}

def memory_markup(chat_id, board, revealed, matched):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    btns = []
    for i in range(len(board)):
        if i in matched:
            btns.append(InlineKeyboardButton("✅", callback_data=f"mm_no_{chat_id}"))
        elif i in revealed:
            btns.append(InlineKeyboardButton(board[i], callback_data=f"mm_no_{chat_id}"))
        else:
            btns.append(InlineKeyboardButton("❓", callback_data=f"mm_pick_{chat_id}_{i}"))
    return InlineKeyboardMarkup([btns[0:4], btns[4:8], btns[8:12], btns[12:16]])

@Client.on_message(filters.group & filters.command(["ذاكرة", "memory"]))
async def memory_start(client, message: Message):
    chat_id = message.chat.id
    if chat_id in memory_games:
        return await message.reply("⚠️ كاين لعبة ذاكرة شغالة")
    memory_games[chat_id] = {
        "board": [],
        "players": {},
        "turn": None,
        "revealed": [],
        "matched": [],
        "turn_order": [],
        "turn_idx": 0,
    }
    await message.reply("🧩 **الذاكرة**\n\n✅ كتب `/انضم2` باش تشارك")

@Client.on_message(filters.group & filters.command(["انضم2", "join2"]))
async def memory_join(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in memory_games:
        return await message.reply("❌ ما كاينش لعبة")
    g = memory_games[chat_id]
    uid = message.from_user.id
    if uid in g["players"]:
        return await message.reply("❌ راك منضم")
    g["players"][uid] = {"name": message.from_user.first_name, "score": 0}
    await message.reply(f"✅ {message.from_user.mention} انضم\n👥 {len(g['players'])} لاعبين")
    if len(g["players"]) >= 2:
        await memory_begin(client, chat_id)

async def memory_begin(client, chat_id):
    g = memory_games[chat_id]
    cards = MEMORY_EMOJIS * 2
    random.shuffle(cards)
    g["board"] = cards
    g["turn_order"] = list(g["players"].keys())
    g["turn_idx"] = 0
    g["turn"] = g["turn_order"][0]
    sent = await client.send_message(
        chat_id,
        f"🧩 دور {g['players'][g['turn']]['name']}",
        reply_markup=memory_markup(chat_id, g["board"], g["revealed"], g["matched"])
    )
    g["last_board_id"] = sent.id

@Client.on_callback_query(filters.regex("^mm_"))
async def memory_callback(client, query):
    if query.data.startswith("mm_no_"):
        return await query.answer("❌")
    parts = query.data.split("_")
    chat_id = int(parts[2])
    pos = int(parts[3])
    uid = query.from_user.id
    if chat_id not in memory_games:
        return await query.answer("❌")
    g = memory_games[chat_id]
    if uid != g["turn"]:
        return await query.answer("⏰ ماشي دورك!", show_alert=True)
    if pos in g["matched"] or pos in g["revealed"]:
        return await query.answer("❌")
    g["revealed"].append(pos)
    await query.answer(f"✅ {g['board'][pos]}")
    if len(g["revealed"]) == 1:
        try:
            await client.edit_message_reply_markup(chat_id, g["last_board_id"], reply_markup=memory_markup(chat_id, g["board"], g["revealed"], g["matched"]))
        except:
            pass
        return
    p1, p2 = g["revealed"][0], g["revealed"][1]
    if g["board"][p1] == g["board"][p2]:
        g["matched"].extend([p1, p2])
        g["players"][uid]["score"] += 1
        await client.send_message(chat_id, f"🎉 {g['players'][uid]['name']} وجد زوجاً! {g['board'][p1]}")
        g["revealed"] = []
        if len(g["matched"]) >= len(g["board"]):
            best = max(g["players"].keys(), key=lambda u: g["players"][u]["score"])
            await client.send_message(chat_id, f"🏆 الفائز: {g['players'][best]['name']}!\n🎁 +10")
            del memory_games[chat_id]
            return
    else:
        await client.send_message(chat_id, f"❌ {g['board'][p1]} ≠ {g['board'][p2]}")
        g["revealed"] = []
        g["turn_idx"] = (g["turn_idx"] + 1) % len(g["turn_order"])
        g["turn"] = g["turn_order"][g["turn_idx"]]
    try:
        await client.edit_message_reply_markup(chat_id, g["last_board_id"], reply_markup=memory_markup(chat_id, g["board"], g["revealed"], g["matched"]))
    except:
        pass

# ============================================================
# 🎯 سرعة رد الفعل
# ============================================================

import time
reaction_games = {}

@Client.on_message(filters.group & filters.command(["رد", "reaction"]))
async def reaction_start(client, message: Message):
    chat_id = message.chat.id
    if chat_id in reaction_games:
        return await message.reply("⚠️ كاين لعبة شغالة")
    reaction_games[chat_id] = {"clicked": {}, "start_time": None, "msg_id": None}
    await message.reply("🎯 **رد الفعل!**\n\n⚡ انتظر...")
    import asyncio
    await asyncio.sleep(3)
    delay = random.uniform(2, 6)
    await asyncio.sleep(delay)
    if chat_id not in reaction_games:
        return
    g = reaction_games[chat_id]
    g["start_time"] = time.time()
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    sent = await message.reply(
        "⚡ **اضغط!**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚡ اضغط!", callback_data=f"rx_click_{chat_id}")]])
    )
    g["msg_id"] = sent.id

@Client.on_callback_query(filters.regex("^rx_click_"))
async def reaction_callback(client, query):
    chat_id = int(query.data.split("_")[2])
    uid = query.from_user.id
    if chat_id not in reaction_games:
        return await query.answer("❌")
    g = reaction_games[chat_id]
    if uid in g["clicked"]:
        return await query.answer("✅")
    g["clicked"][uid] = time.time()
    await query.answer("⚡")
    if len(g["clicked"]) == 1:
        import asyncio
        await asyncio.sleep(3)
        if chat_id not in reaction_games:
            return
        g2 = reaction_games[chat_id]
        sc = sorted(g2["clicked"].items(), key=lambda x: x[1])
        txt = "🏆 **الترتيب:**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (u, t) in enumerate(sc[:3]):
            ms = int((t - g2["start_time"]) * 1000)
            txt += f"{medals[i]} [User](tg://user?id={u}) — {ms}ms\n"
        await client.send_message(chat_id, txt)
        del reaction_games[chat_id]

# ============================================================
# 🎲 النرد
# ============================================================

@Client.on_message(filters.group & filters.command(["نرد", "dice"]))
async def dice_game(client, message: Message):
    user = random.randint(1, 6)
    bot_val = random.randint(1, 6)
    if user > bot_val:
        result = "🎉 ربحت!"
    elif user < bot_val:
        result = "😢 خسرت!"
    else:
        result = "🤝 تعادل!"
    await message.reply(f"🎲 **النرد**\n\n• نتا: {user}\n• البوت: {bot_val}\n\n{result}")

# ============================================================
# ✊ حجرة ورقة مقص
# ============================================================

@Client.on_message(filters.group & filters.command(["حجرة", "rock"]))
async def rps_game(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("🎮 **حجرة ورقة مقص**\n\nاكتب: `/حجرة [حجرة/ورقة/مقص]`")
    choice = message.command[1]
    choices = ["حجرة", "ورقة", "مقص"]
    if choice not in choices:
        return await message.reply(f"❌ اختار من: {'، '.join(choices)}")
    bot_val = random.choice(choices)
    if choice == bot_val:
        result = "🤝 تعادل!"
    elif (choice == "حجرة" and bot_val == "مقص") or \
         (choice == "ورقة" and bot_val == "حجرة") or \
         (choice == "مقص" and bot_val == "ورقة"):
        result = "🎉 ربحت!"
    else:
        result = "😢 خسرت!"
    await message.reply(f"🎮 **حجرة ورقة مقص**\n\n• نتا: {choice}\n• البوت: {bot_val}\n\n{result}")

# ============================================================
# ❓ سؤال وجواب
# ============================================================

QUESTIONS = [
    ("ما هي عاصمة الجزائر؟", "الجزائر"),
    ("كم عدد أيام السنة؟", "365"),
    ("ما هو أكبر كوكب؟", "المشتري"),
    ("كم عدد الصلوات؟", "5"),
    ("ما هي أطول سورة؟", "البقرة"),
    ("ما هو أسرع حيوان؟", "الفهد"),
]

active_quiz = {}

@Client.on_message(filters.group & filters.command(["سؤال", "quiz"]))
async def quiz_start(client, message: Message):
    if message.chat.id in active_quiz:
        return await message.reply("⚠️ كاين سؤال شغال")
    q, a = random.choice(QUESTIONS)
    active_quiz[message.chat.id] = a
    await message.reply(f"❓ **سؤال:**\n\n{q}\n\nاكتب `/جواب [الجواب]`")

@Client.on_message(filters.group & filters.command(["جواب", "answer"]))
async def quiz_answer(client, message: Message):
    if message.chat.id not in active_quiz:
        return await message.reply("❌ ما كاينش سؤال")
    if len(message.command) < 2:
        return await message.reply("❌ اكتب: `/جواب الجواب`")
    ans = message.text.split(None, 1)[1]
    correct = active_quiz[message.chat.id]
    if ans.lower() == correct.lower():
        del active_quiz[message.chat.id]
        await message.reply(f"🎉 صح! {message.from_user.mention}\nالجواب: {correct}")
    else:
        await message.reply("❌ غلط")

# ============================================================
# 🔢 لعبة العد
# ============================================================

COUNTING = {}

@Client.on_message(filters.group & filters.command(["عد", "count"]))
async def counting_start(client, message: Message):
    COUNTING[message.chat.id] = 0
    await message.reply("🎮 **لعبة العد**\n\nاكتب `/زيد` باش تزيد الرقم")

@Client.on_message(filters.group & filters.command(["زيد", "add"]))
async def counting_add(client, message: Message):
    if message.chat.id not in COUNTING:
        return await message.reply("❌ اكتب `/عد` باش تبدا")
    COUNTING[message.chat.id] += 1
    await message.reply(f"🔢 العدد: **{COUNTING[message.chat.id]}**")
