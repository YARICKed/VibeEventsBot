import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

#ENV 
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")

# Канал куда бот будет публиковать посты командой /post
# В .env: POST_CHANNEL=@vibe_events_party  (или числовой id -100...)
POST_CHANNEL = os.getenv("POST_CHANNEL", "").strip()
if not POST_CHANNEL:
    raise RuntimeError("❌ POST_CHANNEL не найден в .env")

# НАСТРОЙКИ
ADMIN_IDS = []
raw_admins = os.getenv("ADMIN_IDS", "")
for x in raw_admins.split(","):
    x = x.strip()
    if x.isdigit():
        ADMIN_IDS.append(int(x))

USERS_FILE = "/app/users.txt"
GIVEAWAY_FILE = "/app/giveaway.txt"

QTICKETS_URL = os.getenv(
    "QTICKETS_URL",
    "https://t.me/QticketsBuyBot/buy?startapp=211242"
)

REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL")
if not REQUIRED_CHANNEL:
    raise RuntimeError("❌ REQUIRED_CHANNEL не найден в .env")

REQUIRED_CHAT_ID = os.getenv("REQUIRED_CHAT_ID")
if not REQUIRED_CHAT_ID:
    raise RuntimeError("❌ REQUIRED_CHAT_ID не найден в .env")
REQUIRED_CHAT_ID = int(REQUIRED_CHAT_ID)


CHANNEL_LINK = os.getenv("CHANNEL_LINK")
if not CHANNEL_LINK:
    raise RuntimeError("❌ CHANNEL_LINK не найден в .env")

CHAT_LINK = os.getenv("CHAT_LINK")
if not CHAT_LINK:
    raise RuntimeError("❌ CHAT_LINK не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# КЛАВИАТУРЫ

def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Мероприятия", callback_data="events")],
        [InlineKeyboardButton(text="🎟 Купить билет", url=QTICKETS_URL)],
        [
            InlineKeyboardButton(text="📍 Локация", callback_data="location"),
            InlineKeyboardButton(text="💃 Dress code", callback_data="dress"),
        ],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

def participate_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Участвовать", callback_data="participate")]
    ])

def requirements_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Вступить в чат", url=CHAT_LINK)],
        [InlineKeyboardButton(text="✅ Проверить участие", callback_data="participate")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def events_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Купить билет", url=QTICKETS_URL)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
    ])

def ticket_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Купить билет", url=QTICKETS_URL)]
    ])

# ТЕКСТЫ 

MAIN_TEXT = (
    "❤️‍🔥 *VIBE EVENTS*\n\n"
    "Пространство для тех, кто чувствует ритм.\n"
    "Громко, красиво и по-настоящему.\n\n"
    "Готов(а) к этой ночи?"
)

EVENTS_CAPTION = (
    "🎉 *VALENTINE’S DAY*\n\n"
    "📅 14 февраля\n"
    "🕒 23:00 — 05:00\n"
    "📍 Москва | Лофт *«Нашедший себя»*\n\n"
    "DJ SET • DANCE BATTLE • FREE BAR\n"
    "SIGNAL BRACELETS • VIP ZONE"
)

GIVEAWAY_TEXT = (
    "🎁 *Розыгрыш*\n\n"
    "Условия участия:\n"
    "1) Подписаться на канал\n"
    "2) Быть в чате\n\n"
    "Нажми 🎁 *Участвовать* — бот проверит автоматически ✅"
)

LOCATION_TEXT = (
    "📍 *Москва*\n\n"
    "Точный адрес придёт после покупки билета 🎟"
)

DRESS_TEXT = (
    "💃 *Dress code:*\n\n"
    "White 🤍 / Pink 💗\n"
    "Red ❤️ / Black 🖤"
)

SUPPORT_TEXT = (
    "🆘 *Поддержка:*\n\n"
    "[Написать менеджеру](https://t.me/gool_d)"
)

# ФАЙЛЫ 

def ensure_file(path: str):
    if not os.path.exists(path):
        open(path, "w", encoding="utf-8").close()

def save_user(user: types.User):
    ensure_file(USERS_FILE)

    user_id = str(user.id)
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    last_name = user.last_name or "—"
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        rows = f.read().splitlines()

    for r in rows:
        if r.startswith(user_id + "|"):
            return

    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}|{username}|{first_name}|{last_name}|{date}\n")

def save_giveaway(user: types.User) -> bool:
    ensure_file(GIVEAWAY_FILE)

    user_id = str(user.id)
    username = f"@{user.username}" if user.username else "—"
    first_name = user.first_name or "—"
    last_name = user.last_name or "—"
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(GIVEAWAY_FILE, "r", encoding="utf-8") as f:
        rows = f.read().splitlines()

    for r in rows:
        if r.startswith(user_id + "|"):
            return False

    with open(GIVEAWAY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}|{username}|{first_name}|{last_name}|{date}\n")

    return True

def load_user_ids():
    ensure_file(USERS_FILE)
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        rows = f.read().splitlines()

    ids = []
    for r in rows:
        part = (r.split("|", 1)[0] if r else "").strip()
        if part.isdigit():
            ids.append(int(part))
    return ids

# ПРОВЕРКА ПОДПИСОК

async def is_member(user_id: int, chat_id) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

# /start 

@dp.message(CommandStart())
async def start(message: types.Message):
    save_user(message.from_user)

    arg = ""
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            arg = parts[1].strip().lower()

    if arg == "giveaway":
        await message.answer(GIVEAWAY_TEXT, reply_markup=participate_keyboard(), parse_mode="Markdown")
        return

    await message.answer(MAIN_TEXT, reply_markup=main_keyboard(), parse_mode="Markdown")

#  /chatid (debug) 

@dp.message(lambda m: m.text == "/chatid")
async def chatid(message: types.Message):
    await message.answer(f"Chat ID этого чата:\n\n`{message.chat.id}`", parse_mode="Markdown")

#  /post (АДМИН)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@dp.message(lambda m: m.text and m.text.startswith("/post"))
async def post_text(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    text = message.text.replace("/post", "", 1).strip()

    if not text:
        await message.answer("❌ Напиши текст после /post")
        return

    try:
        await bot.send_message(
            chat_id=POST_CHANNEL,
            text=text,
            parse_mode="HTML",
            reply_markup=participate_keyboard(),
            disable_web_page_preview=True
        )

        await message.answer("✅ Пост опубликован в канал")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(lambda m: m.photo and m.caption and m.caption.startswith("/post"))
async def post_photo(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    text = message.caption.replace("/post", "", 1).strip()
    file_id = message.photo[-1].file_id

    try:
        await bot.send_photo(
            chat_id=POST_CHANNEL,
            photo=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=participate_keyboard()
        )

        await message.answer("✅ Фото опубликовано в канал")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(lambda m: m.video and m.caption and m.caption.startswith("/post"))
async def post_video(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    text = message.caption.replace("/post", "", 1).strip()
    file_id = message.video.file_id

    try:
        await bot.send_video(
            chat_id=POST_CHANNEL,
            video=file_id,
            caption=text,
            parse_mode="HTML",
            reply_markup=participate_keyboard()
        )

        await message.answer("✅ Видео опубликовано в канал")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

#  EVENTS

@dp.callback_query(lambda c: c.data == "events")
async def events(call: types.CallbackQuery):
    try:
        await call.message.delete()
    except Exception:
        pass

    await call.message.answer_photo(
        FSInputFile("Afisha_aliluya.jpg"),
        caption=EVENTS_CAPTION,
        parse_mode="Markdown",
        reply_markup=events_keyboard()
    )
    await call.answer()

# PARTICIPATE 

@dp.callback_query(lambda c: c.data == "participate")
async def participate(call: types.CallbackQuery):
    user_id = call.from_user.id

    ok1 = await is_member(user_id, REQUIRED_CHANNEL)
    ok2 = await is_member(user_id, REQUIRED_CHAT_ID)

    if ok1 and ok2:
        added = save_giveaway(call.from_user)
        msg = "✅ Ты участвуешь! 🎉" if added else "✅ Ты уже участвуешь! 🎉"

        await call.answer(msg, show_alert=True)

        try:
            await bot.send_message(user_id, msg, parse_mode="Markdown")
        except Exception:
            pass
        return

    missing = []
    if not ok1:
        missing.append(f"❌ Канал: {REQUIRED_CHANNEL}")
    if not ok2:
        missing.append("❌ Чат: участие не найдено")

    text = (
        "❌ Не все условия выполнены\n\n"
        + "\n".join(missing)
        + "\n\nПодпишись/вступи и нажми ✅ *Проверить участие* ещё раз."
    )

    await call.answer("❌ Не выполнены условия", show_alert=True)

    try:
        await bot.send_message(
            user_id,
            text,
            reply_markup=requirements_keyboard(),
            parse_mode="Markdown"
        )
    except Exception:
        await call.answer("Напиши боту /start в личку, чтобы я мог прислать проверку ✅", show_alert=True)

# MENU BUTTONS

@dp.callback_query(lambda c: c.data in ("location", "dress", "support", "back"))
async def callbacks(call: types.CallbackQuery):
    texts = {
        "location": LOCATION_TEXT,
        "dress": DRESS_TEXT,
        "support": SUPPORT_TEXT,
    }

    if call.data == "back":
        try:
            await call.message.delete()
        except Exception:
            pass

        await call.message.answer(MAIN_TEXT, reply_markup=main_keyboard(), parse_mode="Markdown")
        await call.answer()
        return

    try:
        await call.message.delete()
    except Exception:
        pass

    await call.message.answer(texts[call.data], reply_markup=back_keyboard(), parse_mode="Markdown")
    await call.answer()

# /users (админ)

@dp.message(lambda m: m.text == "/users")
async def users(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    ensure_file(USERS_FILE)
    await message.answer_document(FSInputFile(USERS_FILE), caption="👥 Пользователи")

# /giveaway (админ)

@dp.message(lambda m: m.text == "/giveaway")
async def giveaway(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    ensure_file(GIVEAWAY_FILE)

    # если пусто — говорим текстом
    with open(GIVEAWAY_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        await message.answer("🎁 Участников пока нет")
        return

    await message.answer_document(FSInputFile(GIVEAWAY_FILE), caption="🎁 Участники")

# SEND (админ)

def parse_send(raw: str):
    raw = (raw or "").strip()
    use_button = raw.startswith("/send button")
    text = raw.replace("/send button", "", 1).replace("/send", "", 1).strip()
    return use_button, text

@dp.message(lambda m: m.text and m.text.startswith("/send"))
async def send_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    use_button, text = parse_send(message.text)
    if not text:
        await message.answer("❌ Добавь текст\n\nПример:\n/send Привет всем")
        return

    kb = ticket_keyboard() if use_button else None
    users = load_user_ids()

    sent = 0
    for uid in users:
        try:
            await bot.send_message(uid, text, parse_mode="Markdown", reply_markup=kb)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(f"✅ Отправлено: {sent}")

@dp.message(lambda m: m.photo and m.caption and m.caption.startswith("/send"))
async def send_photo(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    use_button, text = parse_send(message.caption)
    if not text:
        await message.answer("❌ Добавь текст в подпись после /send\n\nПример:\n(фото)\n/send Привет всем")
        return

    kb = ticket_keyboard() if use_button else None
    users = load_user_ids()
    file_id = message.photo[-1].file_id

    sent = 0
    for uid in users:
        try:
            await bot.send_photo(uid, file_id, caption=text, parse_mode="Markdown", reply_markup=kb)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(f"✅ Фото отправлено: {sent}")

@dp.message(lambda m: m.video and m.caption and m.caption.startswith("/send"))
async def send_video(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    use_button, text = parse_send(message.caption)
    if not text:
        await message.answer("❌ Добавь текст в подпись после /send\n\nПример:\n(видео)\n/send Привет всем")
        return

    kb = ticket_keyboard() if use_button else None
    users = load_user_ids()
    file_id = message.video.file_id

    sent = 0
    for uid in users:
        try:
            await bot.send_video(uid, file_id, caption=text, parse_mode="Markdown", reply_markup=kb)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(f"✅ Видео отправлено: {sent}")

    # DEBUG ПРОВЕРКА (/checkme)

@dp.message(lambda m: m.text == "/checkme")
async def checkme(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        ch = await bot.get_chat_member(REQUIRED_CHANNEL, message.from_user.id)
        ch_status = ch.status
    except Exception as e:
        ch_status = f"ERROR: {e}"

    try:
        gr = await bot.get_chat_member(REQUIRED_CHAT_ID, message.from_user.id)
        gr_status = gr.status
    except Exception as e:
        gr_status = f"ERROR: {e}"

    await message.answer(f"CHANNEL status: {ch_status}\nCHAT status: {gr_status}")

# START BOT

async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())