import requests
import json
import threading
import time
import random
from datetime import datetime

# ========== КОНФИГ ==========
BOT_TOKEN = "8655886367:AAGQMnYq2OEGI50vn2Z1TWe1P--zp-zydr0"  # ЗАМЕНИТЕ НА СВОЙ ТОКЕН!
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Хранилище данных пользователей
user_data = {}

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С TELEGRAM API ==========
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    """Отправка сообщения"""
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Ошибка: {e}")

def send_callback_answer(callback_id, text=None, show_alert=False):
    """Ответ на callback запрос"""
    url = f"{API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def edit_message(chat_id, message_id, text, reply_markup=None):
    """Редактирование сообщения"""
    url = f"{API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception:
        pass

def delete_message(chat_id, message_id):
    """Удаление сообщения"""
    url = f"{API_URL}/deleteMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "message_id": message_id}, timeout=5)
    except Exception:
        pass

# ========== КЛАВИАТУРЫ ==========
def main_menu_keyboard():
    return {
        "keyboard": [
            [{"text": "🚕 Работа / задания"}],
            [{"text": "👤 Мой профиль"}],
            [{"text": "🔄 Сбросить персонажа"}]
        ],
        "resize_keyboard": True
    }

def cancel_keyboard():
    return {
        "keyboard": [[{"text": "◀ Отмена"}]],
        "resize_keyboard": True
    }

def skin_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "светлый", "callback_data": "skin_light"}],
            [{"text": "тёмный", "callback_data": "skin_dark"}],
            [{"text": "я не мужик 😂", "callback_data": "skin_uni"}]
        ]
    }

def hair_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "Классика", "callback_data": "hair_classic"},
             {"text": "Андеркат", "callback_data": "hair_under"}],
            [{"text": "Дреды", "callback_data": "hair_dreads"},
             {"text": "Лысый", "callback_data": "hair_bald"}],
            [{"text": "ничего не нравится", "callback_data": "hair_none"}]
        ]
    }

def car_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "TAX2", "callback_data": "car_wrong"},
             {"text": "TAX5", "callback_data": "car_wrong"},
             {"text": "TAX3 (твоя)", "callback_data": "car_correct"}],
            [{"text": "TAX4", "callback_data": "car_wrong"},
             {"text": "TAX9", "callback_data": "car_wrong"},
             {"text": "TAX1", "callback_data": "car_wrong"}],
            [{"text": "◀ Назад", "callback_data": "back_to_work"}]
        ]
    }

def trip_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "✅ Высадить пассажира", "callback_data": "finish_trip"}]
        ]
    }

# ========== ОБРАБОТКА КОМАНД ==========
def process_start(chat_id, user_id):
    if user_id in user_data and user_data[user_id].get("in_game"):
        p = user_data[user_id]
        send_message(chat_id, 
            f"👋 С возвращением, {p['name']}!\n"
            f"💰 Баланс: ${p['money']:,}\n"
            f"📋 Задание: {'✅ выполнено' if p.get('task_done') else 'сделать 1 поездку таксиста'}",
            reply_markup=main_menu_keyboard())
    else:
        send_message(chat_id,
            "🤖 *bot бандит*\n\n"
            "Это игра прямо в Telegram.\n"
            "💰 Можно зарабатывать деньги, делать бизнес, покупать тачки и недвижку.\n\n"
            "Давай зарегистрируем твоего персонажа!",
            parse_mode="Markdown")
        send_message(chat_id, "Выбери цвет кожи:", reply_markup=skin_keyboard())

def process_profile(chat_id, user_id):
    p = user_data.get(user_id, {})
    if not p.get("in_game"):
        send_message(chat_id, "Ты ещё не зарегистрирован. Напиши /start", reply_markup=main_menu_keyboard())
        return
    send_message(chat_id,
        f"👤 *{p['name']}*\n"
        f"🎨 Кожа: {p['skin']}\n"
        f"💇 Причёска: {p['hair']}\n"
        f"💰 Деньги: ${p['money']:,}\n"
        f"🚕 Поездок таксистом: {p.get('taxi_trips', 0)}\n"
        f"📋 Задание: {'✅ выполнено' if p.get('task_done') else 'сделать 1 поездку таксиста'}",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard())

def process_reset(chat_id, user_id):
    if user_id in user_data:
        del user_data[user_id]
    send_message(chat_id, "🔄 Персонаж сброшен. Напиши /start, чтобы создать нового.", reply_markup={"remove_keyboard": True})

def process_work_menu(chat_id, user_id):
    p = user_data.get(user_id, {})
    if not p.get("in_game"):
        send_message(chat_id, "Сначала зарегистрируйся: /start")
        return
    send_message(chat_id, "🚕 *Работа таксиста*\n\n"
        f"Твой автомобиль: Cabbie\n"
        f"Поездок до выполнения задания: {0 if p.get('task_done') else 1}\n\n"
        "Выбери машину:",
        parse_mode="Markdown",
        reply_markup=car_keyboard())

# ========== ОБРАБОТКА CALLBACK ==========
user_trips = {}  # user_id -> {"passenger", "destination", "end_time", "message_id"}

def process_callback(callback):
    data = callback["data"]
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]
    user_id = callback["from"]["id"]
    callback_id = callback["id"]

    # Регистрация - выбор кожи
    if data == "skin_light":
        user_data[user_id] = {"skin": "светлый", "reg_step": "hair"}
        send_callback_answer(callback_id)
        edit_message(chat_id, message_id, "Теперь выбери причёску:", reply_markup=hair_keyboard())
    elif data == "skin_dark":
        user_data[user_id] = {"skin": "тёмный", "reg_step": "hair"}
        send_callback_answer(callback_id)
        edit_message(chat_id, message_id, "Теперь выбери причёску:", reply_markup=hair_keyboard())
    elif data == "skin_uni":
        user_data[user_id] = {"skin": "😜 унисекс", "reg_step": "hair"}
        send_callback_answer(callback_id)
        edit_message(chat_id, message_id, "Теперь выбери причёску:", reply_markup=hair_keyboard())
    
    # Выбор причёски
    elif data in ["hair_classic", "hair_under", "hair_dreads", "hair_bald", "hair_none"]:
        hair_map = {
            "hair_classic": "Классика",
            "hair_under": "Андеркат", 
            "hair_dreads": "Дреды",
            "hair_bald": "Лысый",
            "hair_none": "😎 бунтарская"
        }
        user_data[user_id]["hair"] = hair_map[data]
        user_data[user_id]["reg_step"] = "name"
        send_callback_answer(callback_id)
        edit_message(chat_id, message_id, "✏️ Отлично! Теперь напиши, как я буду тебя называть (просто отправь сообщение с именем):", reply_markup=None)
    
    # Работа таксиста - выбор машины
    elif data == "car_correct":
        send_callback_answer(callback_id, "✅ Ты взял ключи от своей ласточки!")
        delete_message(chat_id, message_id)
        start_trip(chat_id, user_id)
    elif data == "car_wrong":
        send_callback_answer(callback_id, "❌ Не та машина!", show_alert=True)
        edit_message(chat_id, message_id, "😵 Ты теребил замок чужого такси, клиент уехал.\nПопробуй ещё раз:", reply_markup=car_keyboard())
    elif data == "back_to_work":
        send_callback_answer(callback_id)
        delete_message(chat_id, message_id)
        process_work_menu(chat_id, user_id)
    
    # Завершение поездки
    elif data == "finish_trip":
        trip = user_trips.get(user_id)
        if not trip:
            send_callback_answer(callback_id, "Нет активной поездки!")
            return
        
        now = time.time()
        if now < trip["end_time"]:
            remaining = int(trip["end_time"] - now)
            send_callback_answer(callback_id, f"⏳ Ещё {remaining} сек. Подождите!", show_alert=True)
            return
        
        # Завершаем поездку
        earnings = 2500
        p = user_data.get(user_id, {})
        p["money"] = p.get("money", 50000) + earnings
        p["taxi_trips"] = p.get("taxi_trips", 0) + 1
        
        task_completed = False
        if not p.get("task_done") and p["taxi_trips"] >= 1:
            p["task_done"] = True
            p["money"] += 50000
            task_completed = True
        
        send_callback_answer(callback_id, f"✅ Поездка завершена! +${earnings}")
        
        msg = f"✅ Вы высадили пассажира *{trip['passenger']}*.\n💰 Заработано: ${earnings:,}\n💵 Баланс: ${p['money']:,}\n🚕 Всего поездок: {p['taxi_trips']}"
        if task_completed:
            msg += "\n\n🎉 *Задание выполнено!* +$50,000\nТебе открыты другие работы!"
        
        send_message(chat_id, msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        delete_message(chat_id, trip.get("trip_message_id", message_id))
        del user_trips[user_id]

def start_trip(chat_id, user_id):
    passengers = ["Писюн", "Джек Воробей", "Мистер Кэш", "Леди Удача", "Босс", "Серёга"]
    destinations = ["РОДИНА-МАТУШКА", "Аэропорт", "Казино Royale", "Пентхаус", "Полицейский участок", "Пляж"]
    passenger = random.choice(passengers)
    destination = random.choice(destinations)
    travel_time = 5  # секунд
    
    sent = send_message(chat_id,
        f"🚕 К тебе подсел *{passenger}*.\n"
        f"Едем в город *{destination}*. Прибудем через {travel_time} сек.\n\n"
        "Ты можешь общаться с пассажиром через чат.",
        parse_mode="Markdown",
        reply_markup=trip_keyboard())
    
    # Тут нужно получить message_id, но для простоты сохраняем в словарь
    user_trips[user_id] = {
        "passenger": passenger,
        "destination": destination,
        "end_time": time.time() + travel_time,
        "trip_message_id": None
    }

# ========== ОСНОВНОЙ ЦИКЛ ==========
def process_updates():
    last_update_id = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates?timeout=30&offset={last_update_id + 1}"
            response = requests.get(url, timeout=35)
            updates = response.json()
            
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"]
                    
                    # Обработка сообщений
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        user_id = msg["from"]["id"]
                        text = msg.get("text", "")
                        
                        if text == "/start":
                            process_start(chat_id, user_id)
                        elif text == "👤 Мой профиль":
                            process_profile(chat_id, user_id)
                        elif text == "🔄 Сбросить персонажа":
                            process_reset(chat_id, user_id)
                        elif text == "🚕 Работа / задания":
                            process_work_menu(chat_id, user_id)
                        elif text == "◀ Отмена":
                            send_message(chat_id, "Действие отменено.", reply_markup=main_menu_keyboard())
                        elif user_id in user_data and user_data[user_id].get("reg_step") == "name":
                            # Сохраняем имя при регистрации
                            user_data[user_id]["name"] = text[:30]
                            user_data[user_id]["in_game"] = True
                            user_data[user_id]["money"] = 50000
                            user_data[user_id]["taxi_trips"] = 0
                            user_data[user_id]["task_done"] = False
                            send_message(chat_id,
                                f"✨ Отлично, {text}! Регистрация завершена!\n"
                                f"🎨 Кожа: {user_data[user_id]['skin']}\n"
                                f"💇 Причёска: {user_data[user_id]['hair']}\n"
                                f"💰 Стартовый капитал: $50,000\n\n"
                                f"📌 Твоё первое задание: сделать 1 поездку на такси\n"
                                f"Используй кнопку '🚕 Работа / задания'",
                                reply_markup=main_menu_keyboard())
                            del user_data[user_id]["reg_step"]
                        elif user_id in user_trips:
                            # Общение с пассажиром
                            passenger = user_trips[user_id]["passenger"]
                            send_message(chat_id, f"💬 *{passenger}*: «Ха-ха, отличный разговор! Скоро приедем.»", parse_mode="Markdown")
                        else:
                            send_message(chat_id, "Используй кнопки меню.", reply_markup=main_menu_keyboard())
                    
                    # Обработка callback запросов
                    elif "callback_query" in update:
                        process_callback(update["callback_query"])
        
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🤖 Бот запущен!")
    process_updates()
