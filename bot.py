import os
import threading
import random
import json
import logging
import traceback
import time
from aiohttp import web
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

logging.basicConfig(level=logging.INFO)

async def handle_ping(request):
    return web.Response(text="OK")

def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

def start_vk_bot():
    try:
        TOKEN = "vk1.a.gMk75jCPeMk7qkAf-qB2WmBzhsH-_6GdPBHl1RsyP3dfyyHWCJdkZnkzLZYByrCuDYSqbIepYnZGtMyR616QCbVFiZP5KmzYS9VdI5p4lKAFQ58E9Znihb-Z34zFTaq_nvrZykovKolrNvdfB0nIAwjJSu_GGSPxz0fIURKeM7hdFNExG73gxURGuK5oM-xUg8RxdrWi0c0s6_Bs3JxWzg"
        GROUP_ID = 241068675
        ADMIN_ID = 878507317

        print("⏳ Пытаюсь подключиться к ВК...")
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        
        # Проверка токена (вызовет ошибку, если токен мертв)
        print("🔍 Проверяю токен...")
        vk.groups.getById(group_id=GROUP_ID)
        print("✅ Токен валиден")

        longpoll = VkBotLongPoll(vk_session, GROUP_ID)
        print("✅ LongPoll подключен")

        DB_FILE = "bookings.json"
        SERVICES = {"Стрижка": "1000₽", "Стрижка + борода": "1500₽", "Королевское бритьё": "1200₽"}
        TIMES = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        user_states = {}
        user_data = {}

        def save_booking(data):
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    bookings = json.load(f)
            else:
                bookings = []
            bookings.append(data)
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(bookings, f, ensure_ascii=False, indent=2)

        def main_menu_keyboard():
            keyboard = VkKeyboard(one_time=True, inline=False)
            keyboard.add_button("💈 Цены", color=VkKeyboardColor.PRIMARY)
            keyboard.add_button("📍 Адрес", color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("✂️ Записаться", color=VkKeyboardColor.POSITIVE)
            keyboard.add_button("⭐ Отзывы", color=VkKeyboardColor.SECONDARY)
            return keyboard.get_keyboard()

        def service_keyboard():
            keyboard = VkKeyboard(one_time=True, inline=False)
            for service in SERVICES:
                keyboard.add_button(service, color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
            keyboard.add_button("🔙 Назад", color=VkKeyboardColor.SECONDARY)
            return keyboard.get_keyboard()

        def time_keyboard():
            keyboard = VkKeyboard(one_time=True, inline=False)
            row = []
            for i, time in enumerate(TIMES):
                row.append(time)
                if len(row) == 3:
                    for t in row:
                        keyboard.add_button(t, color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    row = []
            if row:
                for t in row:
                    keyboard.add_button(t, color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button("🔙 Назад", color=VkKeyboardColor.SECONDARY)
            return keyboard.get_keyboard()

        def confirm_keyboard():
            keyboard = VkKeyboard(one_time=True, inline=False)
            keyboard.add_button("✅ Подтвердить", color=VkKeyboardColor.POSITIVE)
            keyboard.add_button("❌ Отменить", color=VkKeyboardColor.NEGATIVE)
            return keyboard.get_keyboard()

        def send_message(user_id, text, keyboard=None):
            vk.messages.send(user_id=user_id, message=text, keyboard=keyboard, random_id=random.randint(1, 1000000))

        print("🚀 Бот ВК запущен и слушает сообщения...")
        
        while True:
            try:
                for event in longpoll.listen():
                    # ... (тут весь остальной код обработки сообщений, он не меняется) ...
                    pass # Замени этот pass на свой код из предыдущего сообщения
            except Exception as e:
                print(f"⚠️ Ошибка в цикле LongPoll: {e}")
                time.sleep(5)

    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА БОТА:")
        traceback.print_exc()
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    threading.Thread(target=start_vk_bot, daemon=True).start()
    run_web_server()
