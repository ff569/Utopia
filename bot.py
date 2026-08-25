from aiohttp import web
import threading

def run_web():
    app = web.Application()
    app.router.add_get("/", lambda r: web.Response(text="OK"))
    web.run_app(app, port=10000)

threading.Thread(target=run_web, daemon=True).start()

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import json
import os

TOKEN = "vk1.a.D19ZfgOmb6IvttQL1f7ynd_Bz_n9jSyXZ0YbuEoZJ9AgjzdF0IhXx0UXSpOdvXGw-aFzjiITsdAmgPEq6Sng6CiAvCjx6Htw-5ah3RGKsBoRXcqSSGf2UnmS2cH1wfeoLREoFkqNauODk-gOX67zD9eXDf21bfF0jMWW0A1bgy3Tk5k-Hm0Xzo3nDIYXsnddUK8hzWQuTCvjsPMwULJKWQ"
GROUP_ID = 241068675
ADMIN_ID = 878507317

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

DB_FILE = "bookings.json"

SERVICES = {
    "УСЛУГА_1": "ЦЕНА_1",
    "УСЛУГА_2": "ЦЕНА_2",
    "УСЛУГА_3": "ЦЕНА_3",
}

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
    vk.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard,
        random_id=random.randint(1, 1000000)
    )

def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            msg = event.object.message
            user_id = msg['from_id']
            text = msg['text'].lower()
            
            state = user_states.get(user_id, "main")
            
            if text in ["начать", "start", "привет", "меню"]:
                user_states[user_id] = "main"
                send_message(user_id, 
                    "👤 Добро пожаловать!\n\n"
                    "Выберите действие:", main_menu_keyboard())
            
            elif state == "main":
                if "цена" in text:
                    prices = "💈 Цены:\n\n"
                    for service, price in SERVICES.items():
                        prices += f"{service} — {price}\n"
                    send_message(user_id, prices, main_menu_keyboard())
                
                elif "адрес" in text:
                    send_message(user_id, 
                        "📍 ВСТАВЬ_АДРЕС\n"
                        "🕙 ВСТАВЬ_ВРЕМЯ_РАБОТЫ", main_menu_keyboard())
                
                elif "запис" in text:
                    user_states[user_id] = "choosing_service"
                    send_message(user_id, "Выберите услугу:", service_keyboard())
                
                elif "отзыв" in text:
                    send_message(user_id, 
                        "⭐ ВСТАВЬ_ОТЗЫВЫ", main_menu_keyboard())
                
                else:
                    send_message(user_id, "Напишите «начать»", main_menu_keyboard())
            
            elif state == "choosing_service":
                if text in SERVICES:
                    user_data[user_id] = {"service": text, "price": SERVICES[text]}
                    user_states[user_id] = "choosing_time"
                    send_message(user_id, f"Выбрано: {text} — {SERVICES[text]}\n\nВыберите время:", time_keyboard())
                elif "назад" in text:
                    user_states[user_id] = "main"
                    send_message(user_id, "Главное меню:", main_menu_keyboard())
                else:
                    send_message(user_id, "Выберите услугу из списка:", service_keyboard())
            
            elif state == "choosing_time":
                if text in TIMES:
                    user_data[user_id]["time"] = text
                    user_states[user_id] = "confirming"
                    data = user_data[user_id]
                    send_message(user_id, 
                        f"📋 Проверьте запись:\n\n"
                        f"Услуга: {data['service']}\n"
                        f"Цена: {data['price']}\n"
                        f"Время: {data['time']}\n\n"
                        f"Подтвердите:", confirm_keyboard())
                elif "назад" in text:
                    user_states[user_id] = "choosing_service"
                    send_message(user_id, "Выберите услугу:", service_keyboard())
                else:
                    send_message(user_id, "Выберите время из списка:", time_keyboard())
            
            elif state == "confirming":
                if "подтвердить" in text:
                    data = user_data.get(user_id, {})
                    data["user_id"] = user_id
                    save_booking(data)
                    user_states[user_id] = "main"
                    send_message(user_id, 
                        "✅ Запись подтверждена!\n\n"
                        f"Услуга: {data['service']}\n"
                        f"Время: {data['time']}\n\n"
                        "Ждём вас!", main_menu_keyboard())
                    
                    vk.messages.send(
                        user_id=ADMIN_ID,
                        message=f"🆕 Новая запись!\n\n"
                                f"Клиент: @id{user_id}\n"
                                f"Услуга: {data['service']}\n"
                                f"Цена: {data['price']}\n"
                                f"Время: {data['time']}",
                        random_id=random.randint(1, 1000000)
                    )
                
                elif "отменить" in text:
                    user_states[user_id] = "main"
                    send_message(user_id, "Запись отменена.", main_menu_keyboard())
                
                else:
                    send_message(user_id, "Подтвердите или отмените.", confirm_keyboard())

if __name__ == "__main__":
    main()
