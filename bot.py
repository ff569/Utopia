import os
import random
import json
import logging
import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

logging.basicConfig(level=logging.INFO)

# --- ТВОИ ДАННЫЕ ---
TOKEN = "vk1.a.gMk75jCPeMk7qkAf-qB2WmBzhsH-_6GdPBHl1RsyP3dfyyHWCJdkZnkzLZYByrCuDYSqbIepYnZGtMyR616QCbVFiZP5KmzYS9VdI5p4lKAFQ58E9Znihb-Z34zFTaq_nvrZykovKolrNvdfB0nIAwjJSu_GGSPxz0fIURKeM7hdFNExG73gxURGuK5oM-xUg8RxdrWi0c0s6_Bs3JxWzg"
GROUP_ID = 241068675
ADMIN_ID = 878507317

print("⏳ Пытаюсь подключиться к ВК...")
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

try:
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    print("✅ LongPoll подключен")
except Exception as e:
    print(f"❌ Ошибка LongPoll: {e}")
    exit()

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
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object.message
                user_id = msg['from_id']
                text = msg['text'].lower().strip()
                
                state = user_states.get(user_id, "main")
                
                # --- ГЛАВНОЕ МЕНЮ ---
                if text in ["начать", "start", "привет", "меню"]:
                    user_states[user_id] = "main"
                    send_message(user_id, "👤 Добро пожаловать!\n\nВыберите действие:", main_menu_keyboard())
                
                elif state == "main":
                    if "цена" in text:
                        prices = "💈 Цены:\n\n"
                        for service, price in SERVICES.items():
                            prices += f"{service} — {price}\n"
                        send_message(user_id, prices, main_menu_keyboard())
                    
                    elif "адрес" in text:
                        send_message(user_id, "📍 г. Тверь, ул. Вольного Новгорода, 13\n🕙 Ежедневно 10:00–21:00", main_menu_keyboard())
                    
                    elif "запис" in text:
                        user_states[user_id] = "choosing_service"
                        send_message(user_id, "Выберите услугу:", service_keyboard())
                    
                    elif "отзыв" in text:
                        send_message(user_id, "⭐ Отзывы:\n\n«Отличный барбершоп!» — Иван\n«Борода ухожена» — Алексей", main_menu_keyboard())
                    
                    else:
                        send_message(user_id, "Напишите «начать» или выберите кнопку.", main_menu_keyboard())
                
                # --- ВЫБОР УСЛУГИ ---
                elif state == "choosing_service":
                    found_service = None
                    for s in SERVICES:
                        if s.lower() in text:
                            found_service = s
                            break
                    
                    if found_service:
                        user_data[user_id] = {"service": found_service, "price": SERVICES[found_service]}
                        user_states[user_id] = "choosing_time"
                        send_message(user_id, f"Выбрано: {found_service} — {SERVICES[found_service]}\n\nВыберите время:", time_keyboard())
                    elif "назад" in text:
                        user_states[user_id] = "main"
                        send_message(user_id, "Главное меню:", main_menu_keyboard())
                    else:
                        send_message(user_id, "Выберите услугу из списка:", service_keyboard())
                
                # --- ВЫБОР ВРЕМЕНИ ---
                elif state == "choosing_time":
                    if text in TIMES:
                        user_data[user_id]["time"] = text
                        user_states[user_id] = "confirming"
                        data = user_data[user_id]
                        send_message(user_id, f"📋 Проверьте запись:\n\nУслуга: {data['service']}\nЦена: {data['price']}\nВремя: {data['time']}\n\nПодтвердите:", confirm_keyboard())
                    elif "назад" in text:
                        user_states[user_id] = "choosing_service"
                        send_message(user_id, "Выберите услугу:", service_keyboard())
                    else:
                        send_message(user_id, "Выберите время из списка:", time_keyboard())
                
                # --- ПОДТВЕРЖДЕНИЕ ---
                elif state == "confirming":
                    if "подтвердить" in text:
                        data = user_data.get(user_id, {})
                        data["user_id"] = user_id
                        save_booking(data)
                        user_states[user_id] = "main"
                        send_message(user_id, f"✅ Запись подтверждена!\n\nУслуга: {data['service']}\nВремя: {data['time']}\n\nЖдём вас!", main_menu_keyboard())
                        
                        vk.messages.send(user_id=ADMIN_ID, message=f"🆕 Новая запись!\n\nКлиент: @id{user_id}\nУслуга: {data['service']}\nЦена: {data['price']}\nВремя: {data['time']}", random_id=random.randint(1, 1000000))
                    elif "отменить" in text:
                        user_states[user_id] = "main"
                        send_message(user_id, "Запись отменена.", main_menu_keyboard())
                    else:
                        send_message(user_id, "Подтвердите или отмените.", confirm_keyboard())
    except Exception as e:
        print(f"⚠️ Ошибка в цикле: {e}")
        time.sleep(5)
