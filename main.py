import urllib.request
import urllib.parse
import json
import time
import random

# ========== КОНФИГ ==========
BOT_TOKEN = "8655886367:AAGQMnYq2OEGI50vn2Z1TWe1P--zp-zydr0"  # ЗАМЕНИТЕ НА СВОЙ ТОКЕН!

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С TELEGRAM API ==========
def api_request(method, params):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API ошибка {method}: {e}")
        return None

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    params = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    if reply_markup:
        params["reply_markup"] = reply_markup
    return api_request("sendMessage", params)

def send_callback_answer(callback_id, text=None, show_alert=False):
    params = {"callback_query_id": callback_id}
    if text:
        params["text"] = text
        params["show_alert"] = show_alert
    return api_request("answerCallbackQuery", params)

def edit_message_text(chat_id, message_id, text, reply_markup=None):
    params = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        params["reply_markup"] = reply_markup
    return api_request("editMessageText", params)

def delete_message(chat_id, message_id):
    return api_request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

# ========== КЛАВИАТУРЫ ==========
def main_menu():
    return {"keyboard": [[{"text": "🚕 Работа"}, {"text": "👤 Профиль"}], [{"text": "🔄 Сброс"}]], "resize_keyboard": True}

def skin_menu():
    return {"inline_keyboard": [[{"text": "☀️ светлый", "callback_data": "skin_light"}], [{"text": "🌙 тёмный", "callback_data": "skin_dark"}], [{"text": "😜 унисекс", "callback_data": "skin_uni"}]]}

def hair_menu():
    return {"inline_keyboard": [[{"text": "Классика", "callback_data": "hair_c"}, {"text": "Андеркат", "callback_data": "hair_u"}], [{"text": "Дреды", "callback_data": "hair_d"}, {"text": "Лысый", "callback_data": "hair_b"}], [{"text": "не нравится", "callback_data": "hair_n"}]]}

def car_menu():
    return {"inline_keyboard": [[{"text": "TAX2", "callback_data": "w"}, {"text": "TAX5", "callback_data": "w"}, {"text": "✅ TAX3", "callback_data": "ok"}], [{"text": "TAX4", "callback_data": "w"}, {"text": "TAX9", "callback_data": "w"}, {"text": "TAX1", "callback_data": "w"}], [{"text": "◀ Назад", "callback_data": "back"}]]}

def trip_menu():
    return {"inline_keyboard": [[{"text": "✅ Высадить", "callback_data": "finish"}]]}

# ========== ДАННЫЕ ==========
users = {}
trips = {}
reg = {}

# ========== ОБРАБОТКА ==========
def start(chat_id, user_id):
    if user_id in users:
        u = users[user_id]
        send_message(chat_id, f"👋 Привет, {u['name']}!\n💰 Баланс: ${u['money']}\n📋 Задание: {'✅ готово' if u.get('done') else '🚕 1 поездка такси'}", reply_markup=main_menu())
    else:
        send_message(chat_id, "🤖 BOT БАНДИТ\n💰 Игра в Telegram!\n\n🎨 Выбери цвет кожи:", reply_markup=skin_menu())
        reg[user_id] = {}

def profile(chat_id, user_id):
    if user_id not in users:
        send_message(chat_id, "❌ Нет персонажа. /start")
        return
    u = users[user_id]
    send_message(chat_id, f"👤 {u['name']}\n🎨 {u['skin']}\n💇 {u['hair']}\n💰 ${u['money']}\n🚕 Поездок: {u.get('trips',0)}\n📋 {'✅ Задание выполнено' if u.get('done') else '📌 Сделай 1 поездку'}", reply_markup=main_menu())

def reset(chat_id, user_id):
    users.pop(user_id, None)
    trips.pop(user_id, None)
    reg.pop(user_id, None)
    send_message(chat_id, "🔄 Персонаж удалён. /start", reply_markup={"remove_keyboard": True})

def work(chat_id, user_id):
    if user_id not in users:
        send_message(chat_id, "❌ /start")
        return
    u = users[user_id]
    send_message(chat_id, f"🚕 ТАКСИ\n🚗 Cabbie\n📊 Осталось: {0 if u.get('done') else 1}\n\n🔑 Выбери машину:", reply_markup=car_menu())

def start_trip(chat_id, user_id):
    names = ["Писюн", "Джек", "Мистер Кэш", "Леди", "Босс"]
    places = ["РОДИНА", "Аэропорт", "Казино", "Пляж"]
    p = random.choice(names)
    d = random.choice(places)
    res = send_message(chat_id, f"🚕 Пассажир: {p}\n📍 {d}\n⏱ 5 сек.\n💬 Пиши сообщения!", reply_markup=trip_menu())
    if res and res.get("result"):
        trips[user_id] = {"passenger": p, "end": time.time() + 5, "msg_id": res["result"]["message_id"], "chat_id": chat_id}

def finish_trip(user_id, cb_id):
    t = trips.get(user_id)
    if not t:
        send_callback_answer(cb_id, "Нет поездки", True)
        return
    if time.time() < t["end"]:
        send_callback_answer(cb_id, f"⏳ Ещё {int(t['end']-time.time())} сек", True)
        return
    u = users[user_id]
    u["money"] += 2500
    u["trips"] = u.get("trips", 0) + 1
    msg = f"✅ +$2500\n💰 Баланс: ${u['money']}"
    if not u.get("done") and u["trips"] >= 1:
        u["done"] = True
        u["money"] += 50000
        msg += f"\n🎉 ЗАДАНИЕ ВЫПОЛНЕНО! +$50000"
    send_callback_answer(cb_id, "✅ Поездка завершена!")
    send_message(t["chat_id"], msg, reply_markup=main_menu())
    delete_message(t["chat_id"], t["msg_id"])
    del trips[user_id]

def handle_callback(cb):
    cb_id = cb["id"]
    data = cb["data"]
    user_id = cb["from"]["id"]
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    
    if data == "skin_light":
        reg[user_id]["skin"] = "светлый"
        edit_message_text(chat_id, msg_id, "💇 Причёска:", reply_markup=hair_menu())
    elif data == "skin_dark":
        reg[user_id]["skin"] = "тёмный"
        edit_message_text(chat_id, msg_id, "💇 Причёска:", reply_markup=hair_menu())
    elif data == "skin_uni":
        reg[user_id]["skin"] = "унисекс"
        edit_message_text(chat_id, msg_id, "💇 Причёска:", reply_markup=hair_menu())
    elif data in ["hair_c", "hair_u", "hair_d", "hair_b", "hair_n"]:
        hair_map = {"hair_c":"Классика","hair_u":"Андеркат","hair_d":"Дреды","hair_b":"Лысый","hair_n":"Бунтарская"}
        reg[user_id]["hair"] = hair_map[data]
        reg[user_id]["step"] = "name"
        edit_message_text(chat_id, msg_id, "✏️ Напиши своё имя:", reply_markup=None)
    elif data == "ok":
        delete_message(chat_id, msg_id)
        send_callback_answer(cb_id, "✅ Поехали!")
        start_trip(chat_id, user_id)
    elif data == "w":
        send_callback_answer(cb_id, "❌ Не та машина!", True)
        edit_message_text(chat_id, msg_id, "❌ Ошибка! Клиент уехал.\n\n🔑 Попробуй ещё:", reply_markup=car_menu())
    elif data == "back":
        delete_message(chat_id, msg_id)
        work(chat_id, user_id)
    elif data == "finish":
        finish_trip(user_id, cb_id)
    send_callback_answer(cb_id)

# ========== ЗАПУСК ==========
def main():
    last = 0
    print("✅ БОТ ЗАПУЩЕН")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30&offset={last+1}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as r:
                data = json.loads(r.read().decode())
                if data.get("result"):
                    for upd in data["result"]:
                        last = upd["update_id"]
                        if "message" in upd:
                            m = upd["message"]
                            cid = m["chat"]["id"]
                            uid = m["from"]["id"]
                            txt = m.get("text", "")
                            if txt == "/start":
                                start(cid, uid)
                            elif txt == "🚕 Работа":
                                work(cid, uid)
                            elif txt == "👤 Профиль":
                                profile(cid, uid)
                            elif txt == "🔄 Сброс":
                                reset(cid, uid)
                            elif uid in reg and reg[uid].get("step") == "name" and txt:
                                users[uid] = {"name": txt, "skin": reg[uid]["skin"], "hair": reg[uid]["hair"], "money": 50000, "trips": 0, "done": False}
                                send_message(cid, f"✅ ГОТОВО!\n👤 {txt}\n💰 $50000\n🚕 Нажми 'Работа'", reply_markup=main_menu())
                                del reg[uid]
                            elif uid in trips:
                                send_message(cid, f"💬 {trips[uid]['passenger']}: «Ха-ха, отличный разговор!»")
                            elif txt:
                                send_message(cid, "❓ Кнопки меню", reply_markup=main_menu())
                        elif "callback_query" in upd:
                            handle_callback(upd["callback_query"])
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
