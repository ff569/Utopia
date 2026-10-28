import os
import threading
import random
import json
import logging
import traceback
from aiohttp import web
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

logging.basicConfig(level=logging.INFO)

async def handle_ping(request):
    return web.Response(text="OK")

def start_vk_bot():
    try:
        TOKEN = "vk1.a.gMk75jCPeMk7qkAf-qB2WmBzhsH-_6GdPBHl1RsyP3dfyyHWCJdkZnkzLZYByrCuDYSqbIepYnZGtMyR616QCbVFiZP5KmzYS9VdI5p4lKAFQ58E9Znihb-Z34zFTaq_nvrZykovKolrNvdfB0nIAwjJSu_GGSPxz0fIURKeM7hdFNExG73gxURGuK5oM-xUg8RxdrWi0c0s6_Bs3JxWzg"
        GROUP_ID = 241068675
        ADMIN_ID = 878507317

        print("⏳ Пытаюсь подключиться к ВК...")
        vk_session = vk_api.VkApi(token=TOKEN)
        vk = vk_session.get_api()
        
        longpoll = VkBotLongPoll(vk_session, GROUP_ID)
        print("✅ LongPoll подключен")

        # ... (тут весь остальной код бота, он не меняется) ...
        # Для краткости я его пропустил, вставь свои функции и цикл while True

    except Exception as e:
        print("❌ КРИТИЧЕСКАЯ ОШИБКА БОТА:")
        traceback.print_exc()

if __name__ == "__main__":
    threading.Thread(target=start_vk_bot, daemon=True).start()
    
    app = web.Application()
    app.router.add_get("/", handle_ping)
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)
