from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import asyncio
import aiosqlite

TOKEN = "8553551279:AAF9xMhG9xswIbHwtpPBo8fgRplbCjZqAPs"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ===== FILE IDs =====
LESSON1_VIDEO = "BAACAgIAAxkBAAMwaY8_1Kkeed0ODzYmz8SFjnQ1yxwAAq-VAALMM3lIQrvMX2K1hpM6BA"
LESSON2_VIDEO = "BAACAgIAAxkBAAM1aY9CXYkPHgLmMMAhrRyci-hm0XEAAtWVAALMM3lIUrOd-Qu9E6o6BA"
LESSON3_VIDEO = "BAACAgIAAxkBAAM2aY9DEsVmG4FJP_FaVm7b9On5qBUAAu6VAALMM3lIErBo7IQfH806BA"

lesson1_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Получить первый урок", callback_data="lesson1")]
    ]
)

# ===== SQLite =====
DB_PATH = "progress.db"
db: aiosqlite.Connection | None = None

async def init_db():
    global db
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL;")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS user_lessons (
            user_id INTEGER NOT NULL,
            lesson  TEXT    NOT NULL,
            PRIMARY KEY (user_id, lesson)
        );
    """)
    await db.commit()

async def has_lesson(user_id: int, lesson: str) -> bool:
    assert db is not None
    cur = await db.execute(
        "SELECT 1 FROM user_lessons WHERE user_id=? AND lesson=? LIMIT 1",
        (user_id, lesson)
    )
    row = await cur.fetchone()
    await cur.close()
    return row is not None

async def mark_lesson(user_id: int, lesson: str) -> None:
    assert db is not None
    await db.execute(
        "INSERT OR IGNORE INTO user_lessons (user_id, lesson) VALUES (?, ?)",
        (user_id, lesson)
    )
    await db.commit()

# ===== удаляем только предупреждения =====
last_warning_message = {}

async def delete_last_warning(chat_id: int):
    if chat_id in last_warning_message:
        try:
            await bot.delete_message(chat_id, last_warning_message[chat_id])
        except:
            pass

# ================= START =================
@dp.message(CommandStart())
async def start(message: types.Message):
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

    if await has_lesson(user_id, "lesson1"):
        await delete_last_warning(chat_id)
        msg = await callback.message.answer("✅ Первый урок уже выдан.")
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

    if await has_lesson(user_id, "lesson2"):
        await delete_last_warning(chat_id)
        msg = await message.answer("✅ Второй урок уже выдан.")
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

    if await has_lesson(user_id, "lesson3"):
        await delete_last_warning(chat_id)
        msg = await message.answer("✅ Третий урок уже выдан.")
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

# ================= RUN =================
async def main():
    await init_db()
    try:
        await dp.start_polling(bot)
    finally:
        if db is not None:
            await db.close()

if __name__ == "__main__":
    asyncio.run(main())
