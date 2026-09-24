import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import Config
from database import get_user, add_user, users_col

# ============================================================
#                    إعدادات
# ============================================================

MAX_HP = 100
MAX_ENERGY = 3
MIN_PLAYERS = 3
JOIN_TIME = 300
ROUND_TIME = 20

POINTS_ATTACK = 1
POINTS_KILL = 3
POINTS_WIN = 10

MOVES = {
    "attack":  {"name": "⚔️ هجوم",        "dmg": 25, "cost": 0,  "point": POINTS_ATTACK},
    "defense": {"name": "🛡 دفاع",         "dmg": 0,  "cost": 0,  "point": 0},
    "heal":    {"name": "💉 علاج",         "dmg": -30, "cost": 0, "point": 0},
    "spin":    {"name": "🌀 دوران",        "dmg": 35, "cost": 2,  "point": 0},
    "flash":   {"name": "⚡ ضربة خاطفة",   "dmg": 50, "cost": 3,  "point": 0},
    "focus":   {"name": "🎯 تركيز",        "dmg": 0,  "cost": -2, "point": 0},
    "reflect": {"name": "🪃 ارتداد",       "dmg": 20, "cost": 1,  "point": 0},
    "rage":    {"name": "💢 غضب",          "dmg": 40, "cost": 2,  "point": 0},
}

games = {}

# ============================================================
#                    دوال مساعدة
# ============================================================

def hp_bar(hp):
    if hp <= 0:
        return "🟥🟥🟥🟥🟥"
    filled = max(0, min(5, round(hp / 20)))
    return "🟩" * filled + "🟥" * (5 - filled)

def energy_bar(e):
    return "⚡" * max(0, e) + "🔘" * (MAX_ENERGY - max(0, e))

def user_link(uid, name):
    return f'<a href="tg://user?id={uid}">{name}</a>'

async def is_admin(client, chat_id, uid):
    try:
        m = await client.get_chat_member(chat_id, uid)
        from pyrogram.enums import ChatMemberStatus
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

async def get_user_points(uid):
    u = await get_user(uid)
    return u.get("points", 0) if u else 0

async def add_points(uid, amount):
    await users_col.update_one(
        {"user_id": uid},
        {"$inc": {"points": amount}},
        upsert=True
    )

# ============================================================
#                    نص اللعبة
# ============================================================

async def lobby_text(g):
    txt = "🎮 <b>لعبة جديدة:</b> 🥷 <b>ساحة النينجا القتالية</b>\n\n"
    txt += "ℹ️ <b>كيفية اللعب:</b>\n"
    txt += "🗡 كل لاعب يملك <b>100 HP</b> و <b>3 طاقة</b>\n"
    txt += "📍 كل جولة يختار الجميع حركتهم سراً\n\n"
    txt += "<b>📖 الحركات والنقاط:</b>\n"
    txt += f"⚔️ هجوم (25 ضرر) → <b>+{POINTS_ATTACK} نقطة</b>\n"
    txt += f"🛡 دفاع (يصد) → <b>0 نقطة</b>\n"
    txt += f"💉 علاج (+30 HP) → <b>0 نقطة</b>\n"
    txt += "🌀 دوران (35 للكل، طاقة 2) → <b>0 نقطة</b>\n"
    txt += "⚡ خاطفة (50 ضرر، طاقة 3) → <b>0 نقطة</b>\n"
    txt += f"🎯 تركيز (+2 طاقة) → <b>0 نقطة</b>\n"
    txt += "🪃 ارتداد (20 ضرر، طاقة 1) → <b>0 نقطة</b>\n"
    txt += "💢 غضب (40 ضرر + ضرر ذاتي، طاقة 2) → <b>0 نقطة</b>\n\n"
    txt += f"💀 لكل قتل: <b>+{POINTS_KILL} نقاط</b>\n"
    txt += f"🏆 للفوز: <b>+{POINTS_WIN} نقاط</b>\n\n"
    txt += f"👤 بدأها: {user_link(g['starter'], g['starter_name'])}\n"
    txt += "📝 اكتب <code>انا</code> للانضمام\n"
    txt += "▶️ اكتب <code>بدا</code> للبدء\n"
    txt += f"👥 الحد الأدنى: <b>{MIN_PLAYERS} لاعبين</b>\n\n"
    txt += f"👥 <b>اللاعبون ({len(g['players'])}):</b>\n"
    if g['players']:
        for uid, p in g['players'].items():
            pts = await get_user_points(uid)
            txt += f"   • {user_link(uid, p['name'])} — ⭐ {pts}\n"
    else:
        txt += "   لا أحد بعد...\n"
    return txt

def battle_status(g):
    txt = f"⚔️ <b>الجولة {g['round']}</b>\n\n━━━━━━━━━━━━━━\n"
    for uid, p in g['players'].items():
        txt += f"{user_link(uid, p['name'])}\n"
        txt += f"   {hp_bar(p['hp'])} {p['hp']}HP | {energy_bar(p['energy'])}\n"
    txt += "━━━━━━━━━━━━━━\n"
    return txt

def moves_keyboard(chat_id, round_num):
    m = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚔️ هجوم", callback_data=f"mv_attack_{chat_id}_{round_num}"),
            InlineKeyboardButton("🛡 دفاع", callback_data=f"mv_defense_{chat_id}_{round_num}"),
            InlineKeyboardButton("💉 علاج", callback_data=f"mv_heal_{chat_id}_{round_num}"),
        ],
        [
            InlineKeyboardButton("🌀 دوران ⚡2", callback_data=f"mv_spin_{chat_id}_{round_num}"),
            InlineKeyboardButton("⚡ خاطفة ⚡3", callback_data=f"mv_flash_{chat_id}_{round_num}"),
            InlineKeyboardButton("🎯 تركيز", callback_data=f"mv_focus_{chat_id}_{round_num}"),
        ],
        [
            InlineKeyboardButton("🪃 ارتداد ⚡1", callback_data=f"mv_reflect_{chat_id}_{round_num}"),
            InlineKeyboardButton("💢 غضب ⚡2", callback_data=f"mv_rage_{chat_id}_{round_num}"),
        ],
    ])
    return m

# ============================================================
#                    الحلقة الرئيسية
# ============================================================

async def end_game(client, chat_id, reason="", winner_uid=None, winner_name=None):
    g = games.pop(chat_id, None)
    if not g:
        return
    try:
        if g.get('last_msg_id'):
            await client.delete_messages(chat_id, g['last_msg_id'])
    except:
        pass

    if winner_uid:
        await add_points(winner_uid, POINTS_WIN)
        await users_col.update_one(
            {"user_id": winner_uid},
            {"$inc": {"wins": 1}},
            upsert=True
        )
        msg = "╔══════════════════════╗\n"
        msg += "║   🏆 <b>الفائز النهائي</b> 🏆   ║\n"
        msg += "╚══════════════════════╝\n\n"
        msg += f"🥇 {user_link(winner_uid, winner_name)}\n\n"
        msg += f"💬 {reason}\n"
        msg += f"🎁 <b>+{POINTS_WIN} نقطة</b>\n\n"
        pts = await get_user_points(winner_uid)
        msg += f"⭐ رصيده: <b>{pts} نقطة</b>\n\n"
        msg += "🎮 اكتب <code>نينجا</code> لبدء معركة جديدة"
        await client.send_message(chat_id, msg)
    else:
        msg = "╔══════════════════════╗\n"
        msg += "║   🛑 <b>انتهت المعركة</b>   ║\n"
        msg += "╚══════════════════════╝\n\n"
        msg += f"💬 {reason}\n\n"
        msg += "🎮 اكتب <code>نينجا</code> لبدء معركة جديدة"
        await client.send_message(chat_id, msg)

async def check_winner(client, chat_id):
    g = games.get(chat_id)
    if not g:
        return False
    if len(g['players']) == 1:
        wuid = list(g['players'].keys())[0]
        wname = g['players'][wuid]['name']
        await end_game(client, chat_id, "✅ بقي نينجا واحد فقط!", wuid, wname)
        return True
    if len(g['players']) == 0:
        await end_game(client, chat_id, "💀 الجميع سقط!")
        return True
    return False

def pick_target(g, uid):
    targets = [u for u in g['players'] if u != uid and g['players'][u]['hp'] > 0]
    return random.choice(targets) if targets else None

def apply_damage(g, uid, dmg):
    if uid in g['players']:
        g['players'][uid]['hp'] = max(0, g['players'][uid]['hp'] - dmg)

async def run_round(client, chat_id):
    g = games.get(chat_id)
    if not g:
        return
    if await check_winner(client, chat_id):
        return

    try:
        if g.get('last_msg_id'):
            await client.delete_messages(chat_id, g['last_msg_id'])
    except:
        pass

    g['round'] += 1
    g['moves'] = {}

    text = battle_status(g) + f"\n⏰ اختر حركتك ({ROUND_TIME} ثانية)"

    try:
        sent = await client.send_message(chat_id, text, reply_markup=moves_keyboard(chat_id, g['round']))
        g['last_msg_id'] = sent.id
    except Exception as e:
        print(f"خطأ: {e}")
        return

    await asyncio.sleep(ROUND_TIME)

    if chat_id not in games:
        return

    try:
        if g.get('last_msg_id'):
            await client.delete_messages(chat_id, g['last_msg_id'])
    except:
        pass

    log = f"📊 <b>نتائج الجولة {g['round']}</b>\n\n"
    moves = g['moves']

    if not moves:
        log += "😴 لم يختر أحد حركته!\n"

    for uid in list(moves.keys()):
        if uid not in g['players']:
            continue
        p = g['players'][uid]
        move = moves[uid]
        info = MOVES[move]
        p_link = user_link(uid, p['name'])

        if info['cost'] > 0:
            p['energy'] -= info['cost']
        elif info['cost'] < 0:
            p['energy'] = min(MAX_ENERGY, p['energy'] + abs(info['cost']))

        if info.get('point', 0) > 0:
            await add_points(uid, info['point'])

        if move == "attack":
            t = pick_target(g, uid)
            if t:
                t_link = user_link(t, g['players'][t]['name'])
                if g['players'][t].get('defending'):
                    log += f"🛡 {p_link} هاجم لكن {t_link} صدّ!\n"
                else:
                    apply_damage(g, t, info['dmg'])
                    log += f"⚔️ {p_link} → {t_link} (-{info['dmg']}) ⭐+{POINTS_ATTACK}\n"
                    if g['players'][t]['hp'] <= 0:
                        await add_points(uid, POINTS_KILL)
                        log += f"      └─ 💀 +{POINTS_KILL} نقاط!\n"

        elif move == "defense":
            p['defending'] = True
            log += f"🛡 {p_link} دخل في وضع الدفاع\n"

        elif move == "spin":
            for tuid, tp in list(g['players'].items()):
                if tuid != uid:
                    before_hp = tp['hp']
                    apply_damage(g, tuid, info['dmg'])
                    log += f"🌀 {p_link} دار على {user_link(tuid, tp['name'])} (-{info['dmg']})\n"
                    if tp['hp'] <= 0 and before_hp > 0:
                        await add_points(uid, POINTS_KILL)

        elif move == "heal":
            before = p['hp']
            p['hp'] = min(MAX_HP, p['hp'] + 30)
            log += f"💉 {p_link} استعاد +{p['hp'] - before} HP\n"

        elif move == "flash":
            t = pick_target(g, uid)
            if t:
                dmg = info['dmg']
                if g['players'][t].get('defending'):
                    dmg //= 2
                apply_damage(g, t, dmg)
                log += f"⚡ {p_link} خاطفة → {user_link(t, g['players'][t]['name'])} (-{dmg})\n"
                if g['players'][t]['hp'] <= 0:
                    await add_points(uid, POINTS_KILL)

        elif move == "focus":
            log += f"🎯 {p_link} ركّز واستعاد +2 طاقة\n"

        elif move == "reflect":
            t = pick_target(g, uid)
            if t:
                apply_damage(g, t, info['dmg'])
                log += f"🪃 {p_link} ارتد على {user_link(t, g['players'][t]['name'])} (-{info['dmg']})\n"
                if g['players'][t]['hp'] <= 0:
                    await add_points(uid, POINTS_KILL)

        elif move == "rage":
            t = pick_target(g, uid)
            if t:
                dmg = info['dmg']
                if g['players'][t].get('defending'):
                    dmg //= 2
                apply_damage(g, t, dmg)
                log += f"💢 {p_link} غضب على {user_link(t, g['players'][t]['name'])} (-{dmg})\n"
                if g['players'][t]['hp'] <= 0:
                    await add_points(uid, POINTS_KILL)
            apply_damage(g, uid, 15)
            log += f"💢 {p_link} تلقّى ضرر الغضب (-15)\n"

    for uid, p in list(g['players'].items()):
        if uid not in moves:
            log += f"😴 {user_link(uid, p['name'])} تجمد (15 ضرر)\n"
            apply_damage(g, uid, 15)

    for p in g['players'].values():
        p['defending'] = False

    for uid in list(g['players'].keys()):
        if g['players'][uid]['hp'] <= 0:
            log += f"💀 {user_link(uid, g['players'][uid]['name'])} خرج!\n"
            del g['players'][uid]

    log += "\n" + battle_status(g)
    await client.send_message(chat_id, log)

    if g['starter'] not in g['players']:
        await end_game(client, chat_id, f"⚠️ خرج من بدأ اللعبة!")
        return

    if await check_winner(client, chat_id):
        return

    await asyncio.sleep(3)
    asyncio.create_task(run_round(client, chat_id))

# ============================================================
#                    الأوامر
# ============================================================

@Client.on_message(filters.group & filters.regex(r"^نينجا$"))
async def ninja_start(client, message: Message):
    chat_id = message.chat.id
    uid = message.from_user.id
    name = message.from_user.first_name
    await add_user(uid, name, message.from_user.username)

    if chat_id in games:
        g = games[chat_id]
        if g.get('active'):
            return await message.reply("⚠️ هناك معركة جارية!")
        return await message.reply("⚠️ هناك لعبة مفتوحة! اكتب <code>انا</code> أو <code>ايقاف</code>.")

    games[chat_id] = {
        'players': {},
        'starter': uid,
        'starter_name': name,
        'round': 0,
        'moves': {},
        'active': False,
        'last_msg_id': None,
    }
    g = games[chat_id]
    text = await lobby_text(g)
    await message.reply(text)

    asyncio.create_task(join_timer(client, chat_id))

async def join_timer(client, chat_id):
    await asyncio.sleep(JOIN_TIME)
    g = games.get(chat_id)
    if g and not g.get('active'):
        await end_game(client, chat_id, "⏰ انتهى وقت الانضمام!")

@Client.on_message(filters.group & filters.regex(r"^انا$"))
async def ninja_join(client, message: Message):
    chat_id = message.chat.id
    uid = message.from_user.id
    name = message.from_user.first_name

    g = games.get(chat_id)
    if not g:
        return await message.reply("❌ اكتب <code>نينجا</code> أولاً.")
    if g.get('active'):
        return await message.reply("⚠️ المعركة بدأت!")
    if uid in g['players']:
        return await message.reply("⚠️ راك مشارك!")

    await add_user(uid, name, message.from_user.username)

    g['players'][uid] = {
        'name': name,
        'hp': MAX_HP,
        'energy': MAX_ENERGY,
        'defending': False,
    }

    players_list = "\n".join([
        f'   • {user_link(u, p["name"])}'
        for u, p in g['players'].items()
    ])

    await message.reply(
        f"✅ {user_link(uid, name)} انضم\n"
        f"👥 عدد اللاعبين: <b>{len(g['players'])}</b>\n\n"
        f"👤 <b>المنضمون:</b>\n{players_list}"
    )

@Client.on_message(filters.group & filters.regex(r"^بدا$"))
async def ninja_begin(client, message: Message):
    chat_id = message.chat.id
    uid = message.from_user.id

    g = games.get(chat_id)
    if not g:
        return await message.reply("❌ اكتب <code>نينجا</code> أولاً.")
    if g['starter'] != uid:
        return await message.reply("❌ فقط من بدأ اللعبة يمكنه إطلاقها.")
    if len(g['players']) < MIN_PLAYERS:
        return await message.reply(f"❌ تحتاج <b>{MIN_PLAYERS}</b> لاعبين.")
    if g.get('active'):
        return

    g['active'] = True

    players_list = "\n".join([
        f'   • {user_link(u, p["name"])}'
        for u, p in g['players'].items()
    ])

    await message.reply(
        f"🔥 <b>المعركة تبدأ الآن</b>\n\n"
        f"👤 <b>اللاعبون ({len(g['players'])}):</b>\n{players_list}\n\n"
        f"⚔️ استعدوا!"
    )

    await asyncio.sleep(2)
    asyncio.create_task(run_round(client, chat_id))

@Client.on_message(filters.group & filters.regex(r"^ايقاف$"))
async def ninja_stop(client, message: Message):
    chat_id = message.chat.id
    uid = message.from_user.id

    g = games.get(chat_id)
    if not g:
        return await message.reply("لا توجد لعبة.")

    if uid == g['starter']:
        await end_game(client, chat_id, f"🛑 إيقاف بواسطة المنشئ {user_link(uid, message.from_user.first_name)}")
    elif await is_admin(client, chat_id, uid):
        await end_game(client, chat_id, f"🛑 إيقاف بواسطة Admin")
    else:
        await message.reply("❌ فقط من بدأ اللعبة أو Admin يمكنه إيقافها!")

# ============================================================
#                    معالج الحركات
# ============================================================

@Client.on_callback_query(filters.regex("^mv_"))
async def ninja_move(client, query: CallbackQuery):
    parts = query.data.split("_")
    move = parts[1]
    chat_id = int(parts[2])
    round_num = int(parts[3])
    uid = query.from_user.id

    g = games.get(chat_id)
    if not g:
        return await query.answer("❌ ما كاينش لعبة", show_alert=True)
    if uid not in g['players']:
        return await query.answer("❌ ماشي لاعب", show_alert=True)
    if g['round'] != round_num:
        return await query.answer("❌ الجولة تبدلت", show_alert=True)
    if uid in g['moves']:
        return await query.answer("✅ راك اخترت من قبل", show_alert=True)

    info = MOVES[move]
    p = g['players'][uid]
    if p['energy'] < info['cost']:
        return await query.answer(f"❌ ما عندكش طاقة كافية ({info['cost']})", show_alert=True)

    g['moves'][uid] = move
    await query.answer(f"✅ {info['name']}")

# ============================================================
#                    /top و /my_stats
# ============================================================

@Client.on_message(filters.group & filters.command(["top", "الأبطال"]))
async def top_cmd(client, message: Message):
    top_users = []
    async for u in users_col.find({}).sort("points", -1).limit(10):
        top_users.append(u)

    if not top_users:
        return await message.reply("لا توجد إحصائيات.")

    txt = "🏆 <b>أفضل 10 لاعبين</b>\n\n"
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    for i, u in enumerate(top_users):
        txt += f"{medals[i]} {u.get('first_name', 'لاعب')} — ⭐ {u.get('points', 0)}\n"
    await message.reply(txt)

@Client.on_message(filters.group & filters.command(["my_stats", "احصائياتي"]))
async def my_stats(client, message: Message):
    uid = message.from_user.id
    u = await get_user(uid)
    if not u:
        return await message.reply("❌ ما عندكش إحصائيات، لعب أولاً.")
    txt = f"📊 <b>إحصائياتك</b>\n\n"
    txt += f"👤 {u.get('first_name', 'لاعب')}\n"
    txt += f"⭐ النقاط: <b>{u.get('points', 0)}</b>\n"
    txt += f"🏆 الانتصارات: <b>{u.get('wins', 0)}</b>\n"
    await message.reply(txt)

# ============================================================
#                    لوحة الأدمن
# ============================================================

def admin_panel():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 إحصائيات", callback_data="adm_stats")],
        [InlineKeyboardButton("🏆 الأبطال", callback_data="adm_top")],
        [InlineKeyboardButton("❌ إغلاق", callback_data="adm_close")],
    ])

@Client.on_message(filters.private & filters.user(Config.OWNER_ID) & filters.command("admin"))
async def admin_cmd(client, message: Message):
    total_users = await users_col.count_documents({})
    txt = "🎛️ <b>لوحة تحكم الأدمن</b>\n\n"
    txt += f"👥 المستخدمون: <b>{total_users}</b>\n"
    txt += f"🎮 الألعاب الشغالة: <b>{len(games)}</b>"
    await message.reply(txt, reply_markup=admin_panel())

@Client.on_callback_query(filters.regex("^adm_"))
async def admin_callback(client, query: CallbackQuery):
    if query.from_user.id != Config.OWNER_ID:
        return await query.answer("❌ للأدمن فقط", show_alert=True)
    if query.data == "adm_stats":
        total = await users_col.count_documents({})
        await query.message.edit_text(
            f"📊 <b>إحصائيات</b>\n\n👥 {total} مستخدم\n🎮 {len(games)} لعبة",
            reply_markup=admin_panel()
        )
    elif query.data == "adm_top":
        top = []
        async for u in users_col.find({}).sort("points", -1).limit(5):
            top.append(u)
        txt = "🏆 <b>الأبطال</b>\n\n"
        for i, u in enumerate(top, 1):
            txt += f"{i}. {u.get('first_name', '?')} — ⭐ {u.get('points', 0)}\n"
        await query.message.edit_text(txt, reply_markup=admin_panel())
    elif query.data == "adm_close":
        await query.message.delete()
