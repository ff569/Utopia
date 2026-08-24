import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.markdown import bold
import configparser

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка конфигурации
config = configparser.ConfigParser()
config.read('config.ini')
BOT_TOKEN = config['DEFAULT']['BOT_TOKEN']

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура с инлайн-кнопками
keyboard = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)
keyboard.add(
    InlineKeyboardButton(
        text="Связаться",
        url="t.me/📍 г. Тверь, ул. Вольного Новгорода, д. 13"
    ),
    InlineKeyboardButton(
        text="Портфолио",
        url="t.me/📍 г. Тверь, ул. Вольного Новгорода, д. 13"
    ),
    InlineKeyboardButton(
        text="Отзывы",
        callback_data="reviews"
    )
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    info_text = (
        f"{bold('Барбершоп "UTÖPIA"')}\n\n"
        "Услуги: Мужские стрижки, борода и уход.\n"
        "Работаем ежедневно. Запись онлайн за 1 минуту.\n\n"
        "Контакт:\n"
        "@📍 г. Тверь, ул. Вольного Новгорода, д. 13\n"
        "📞 +7 (900) 000-00-00\n"
        "🕙 Ежедневно с 10:00 до 21:00"
    )
    await message.answer(text=info_text, reply_markup=keyboard)

# Обработчик callback-запросов
@dp.callback_query(F.data == "reviews")
async def reviews_handler(callback: CallbackQuery):
    reviews_text = (
        "Вот несколько отзывов наших клиентов:\n\n"
        "★ ★ ★ ★ ★\n"
        "\"Отличный барбершоп! Стрижка выполнена на высшем уровне.\"\n\n"
        "★ ★ ★ ★ ★\n"
        "\"Борода ухожена, атмосфера уютная. Обязательно вернусь!\""
    )
    await callback.message.answer(text=reviews_text)
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
