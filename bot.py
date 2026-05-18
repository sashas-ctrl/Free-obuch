import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from supabase import create_client

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render сам задаёт, вида https://xxx.onrender.com
PORT = int(os.getenv("PORT", "10000"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_KEY is not set")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ===== FILE IDs =====
LESSON1_VIDEO = "BAACAgIAAxkBAAMwaY8_1Kkeed0ODzYmz8SFjnQ1yxwAAq-VAALMM3lIQrvMX2K1hpM6BA"
LESSON2_VIDEO = "BAACAgIAAxkBAAM1aY9CXYkPHgLmMMAhrRyci-hm0XEAAtWVAALMM3lIUrOd-Qu9E6o6BA"
LESSON3_VIDEO = "BAACAgIAAxkBAAM2aY9DEsVmG4FJP_FaVm7b9On5qBUAAu6VAALMM3lIErBo7IQfH806BA"

lesson1_button = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🔥 Получить первый урок", callback_data="lesson1")]]
)

# ===== удаляем только предупреждения (это можно держать в памяти) =====
last_warning_message = {}

async def delete_last_warning(chat_id: int):
    if chat_id in last_warning_message:
        try:
            await bot.delete_message(chat_id, last_warning_message[chat_id])
        except:
            pass

# ===== Supabase helpers (через asyncio.to_thread, чтобы не блокировать event loop) =====
async def upsert_user(user_id: int):
    def _do():
        supabase.table("bot_users").upsert({"user_id": user_id}).execute()
    await asyncio.to_thread(_do)

async def has_lesson(user_id: int, lesson: str) -> bool:
    def _do():
        res = supabase.table("user_lessons").select("lesson").eq("user_id", user_id).eq("lesson", lesson).limit(1).execute()
        return bool(res.data)
    return await asyncio.to_thread(_do)

async def mark_lesson(user_id: int, lesson: str):
    def _do():
        # гарантируем, что пользователь есть
        supabase.table("bot_users").upsert({"user_id": user_id}).execute()
        # записываем урок (если уже есть — не дублируем)
        supabase.table("user_lessons").upsert({"user_id": user_id, "lesson": lesson}).execute()
    await asyncio.to_thread(_do)

# ================= START =================
@dp.message(CommandStart())
async def start(message: types.Message):
    await upsert_user(message.from_user.id)

    await message.answer(
        "<b>Добрейшего дня, мой друг!</b>\n\n"
        "Рад, что ты зашел на моё бесплатное обучение по серому контенту на YouTube💰\n\n"
        "Тебя ждёт 3 урока, в которых ты полностью погрузишься в сферу серого контента и поймешь с чего начать и в каком направлении тебе двигаться!\n\n"
        "<b>Жми на кнопку ниже и начинай смотреть обучение!</b>",
        reply_markup=lesson1_button
    )

# ================= УРОК 1 =================
@dp.callback_query(F.data == "lesson1")
async def lesson1_handler(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    await upsert_user(user_id)

    if await has_lesson(user_id, "lesson1"):
        await delete_last_warning(chat_id)
        msg = await callback.message.answer("✅ Первый урок уже выдан")
        last_warning_message[chat_id] = msg.message_id
        return

    await callback.message.answer_video(
        video=LESSON1_VIDEO,
        caption=(
            "<b>Урок №1. ВЫБОР НИШИ И КАНАЛА</b>\n\n"
            "<b>Что тебя там ждёт?</b>\n"
            "• Узнаешь о Нишах в сером контенте\n"
            "• Как находить и выбирать Ниши\n"
            "• Какие Каналы нужны\n"
            "• С чего начать новичку\n\n"
            "📝 Чтобы получить второй урок, нужно написать кодовое слово из первого урока!\n"
            "@sashablogerr"
        )
    )
    await mark_lesson(user_id, "lesson1")

# ================= УРОК 2 =================
@dp.message(F.text.lower() == "яблоко")
async def lesson2_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    await upsert_user(user_id)

    if await has_lesson(user_id, "lesson2"):
        await delete_last_warning(chat_id)
        msg = await message.answer("✅ Второй урок уже выдан")
        last_warning_message[chat_id] = msg.message_id
        return

    await message.answer_video(
        video=LESSON2_VIDEO,
        caption=(
            "<b>Урок №2. ПРОЛИВ НА КАНАЛЕ</b>\n\n"
            "<b>Что тебя там ждёт?</b>\n"
            "• Из чего состоит пролив\n"
            "• Что необходимо делать для безопасности канала\n"
            "• Критерии дохода для каналов\n\n"
            "📝 Чтобы получить третий урок, нужно написать кодовое слово из второго урока!\n"
            "@sashablogerr"
        )
    )
    await mark_lesson(user_id, "lesson2")

# ================= УРОК 3 =================
@dp.message(F.text.lower() == "ананас")
async def lesson3_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    await upsert_user(user_id)

    if await has_lesson(user_id, "lesson3"):
        await delete_last_warning(chat_id)
        msg = await message.answer("✅ Третий урок уже выдан")
        last_warning_message[chat_id] = msg.message_id
        return

    await message.answer_video(
        video=LESSON3_VIDEO,
        caption=(
            "<b>Урок №3. ПРОЛИВ НА КАНАЛЕ</b>\n\n"
            "<b>Что тебя там ждёт?</b>\n"
            "• Мой способ чистки каналов\n"
            "• Инсайт, который продают за тысячи$\n"
            "• Всё про выплаты\n"
            "• Советы и наставление новичкам\n\n"
            "📝 Надеюсь тебе понравилось обучение и ты подчерпнул для себя что-то полезное!\n"
            "@sashablogerr"
        )
    )
    await mark_lesson(user_id, "lesson3")

# ================= WEBHOOK =================
async def on_startup(app: web.Application):
    # ставим webhook только если Render дал внешний URL
    if BASE_WEBHOOK_URL:
        await bot.set_webhook(
            url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET
        )

async def on_shutdown(app: web.Application):
    try:
        await bot.delete_webhook(drop_pending_updates=False)
    except:
        pass

def create_app() -> web.Application:
    app = web.Application()

    async def health(request):
        # Пингуем Supabase лёгким запросом, чтобы база не уходила в паузу
        try:
            def _ping_db():
                supabase.table("bot_users").select("user_id").limit(1).execute()
            await asyncio.to_thread(_ping_db)
            return web.Response(text="OK")
        except Exception as e:
            # Даже если БД не отвечает — Render всё равно должен оставаться живым
            return web.Response(text=f"OK (db error: {e})", status=200)

    app.router.add_get("/health", health)
    app.router.add_get("/", health)  # чтобы пинги на корень тоже работали

    app.on_startup.append(on_startup)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    ).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=PORT)
