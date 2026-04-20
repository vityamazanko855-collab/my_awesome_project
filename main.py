import urllib.request
import urllib.parse
import json
import time
import random

# ========== ТОКЕН (ЗАМЕНИ НА СВОЙ) ==========
BOT_TOKEN = "8655886367:AAGQMnYq2OEGI50vn2Z1TWe1P--zp-zydr0"

# ========== TELEGRAM API через urllib ==========
def api_call(method, params):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def send_msg(chat_id, text, reply_markup=None, parse_mode=None):
    p = {"chat_id": chat_id, "text": text}
    if parse_mode:
        p["parse_mode"] = parse_mode
    if reply_markup:
        p["reply_markup"] = reply_markup
    return api_call("sendMessage", p)

def send_cb(cb_id, text=None, alert=False):
    p = {"callback_query_id": cb_id}
    if text:
        p["text"] = text
        p["show_alert"] = alert
    return api_call("answerCallbackQuery", p)

def edit_msg(chat_id, msg_id, text, reply_markup=None):
    p = {"chat_id": chat_id, "message_id": msg_id, "text": text}
    if reply_markup:
        p["reply_markup"] = reply_markup
    return api_call("editMessageText", p)

def del_msg(chat_id, msg_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

# ========== КЛАВИАТУРЫ (как на фото) ==========
def main_kb():
    return {"keyboard": [[{"text": "🚕 Работа / задания"}], [{"text": "👤 Профиль"}], [{"text": "🔄 Сбросить персонажа"}]], "resize_keyboard": True}

def skin_kb():
    return {"inline_keyboard": [[{"text": "светлый", "callback_data": "skin_light"}], [{"text": "тёмный", "callback_data": "skin_dark"}], [{"text": "я не мужик 😂", "callback_data": "skin_uni"}]]}

def hair_kb():
    return {"inline_keyboard": [[{"text": "Классика", "callback_data": "h1"}, {"text": "Андеркат", "callback_data": "h2"}], [{"text": "Дреды", "callback_data": "h3"}, {"text": "Лысый", "callback_data": "h4"}], [{"text": "ничего не нравится", "callback_data": "h5"}]]}

def car_kb():
    return {"inline_keyboard": [[{"text": "TAX2", "callback_data": "car_wrong"}, {"text": "TAX5", "callback_data": "car_wrong"}, {"text": "TAX3", "callback_data": "car_correct"}], [{"text": "TAX4", "callback_data": "car_wrong"}, {"text": "TAX9", "callback_data": "car_wrong"}, {"text": "TAX1", "callback_data": "car_wrong"}], [{"text": "◀ Назад", "callback_data": "back_work"}]]}

def trip_kb():
    return {"inline_keyboard": [[{"text": "✅ обновить время / высадить", "callback_data": "finish_trip"}]]}

# ========== ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ ==========
users = {}      # user_id -> {name, skin, hair, money, trips, task_done}
reg_data = {}   # user_id -> {step, skin, hair}
active_trips = {}  # user_id -> {passenger, end_time, msg_id, chat_id}

# ========== КОМАНДЫ И СООБЩЕНИЯ (ТОЧНО КАК НА ФОТО) ==========
def cmd_start(chat_id, user_id):
    if user_id in users and users[user_id].get("in_game"):
        u = users[user_id]
        send_msg(chat_id, f"здравствуй, {u['name']}! на счету у тя ${u['money']:,}.", reply_markup=main_kb())
        send_msg(chat_id, "предлагаю заработать немного денег!\n\n☝️ жми на кнопку \"задания\".", reply_markup=main_kb())
    else:
        send_msg(chat_id, "# bot бандит\n20,977 пользователей\n\nЧто умеет этот бот?\n\nбот бандит — это игра прямо в твоём Telegram-чате.\n\nтут можно зарабатывать деньги, делать бизнес, покупать недвижимость, тачки и шмотки (и многое другое).\n\n20 апреля\n\n/start 13:02\n\nрегистрация\n\nпривет, , вижу у тебя ещё нет человечка в бот бандите!\n\nдавай это исправим.")
        send_msg(chat_id, "✔ создать человечка", reply_markup=skin_kb())
        reg_data[user_id] = {"step": "skin"}

def cmd_profile(chat_id, user_id):
    if user_id not in users:
        send_msg(chat_id, "Ты ещё не зарегистрирован. Напиши /start")
        return
    u = users[user_id]
    send_msg(chat_id, f"👤 {u['name']}\n🎨 {u['skin']}\n💇 {u['hair']}\n💰 ${u['money']:,}\n🚕 Поездок: {u.get('trips', 0)}\n📋 Задание: {'✅ выполнено' if u.get('task_done') else 'сделать 1 поездку таксиста'}", reply_markup=main_kb())

def cmd_reset(chat_id, user_id):
    users.pop(user_id, None)
    reg_data.pop(user_id, None)
    active_trips.pop(user_id, None)
    send_msg(chat_id, "Персонаж сброшен. Напиши /start", reply_markup={"remove_keyboard": True})

def cmd_work(chat_id, user_id):
    if user_id not in users:
        send_msg(chat_id, "Сначала регистрация: /start")
        return
    u = users[user_id]
    send_msg(chat_id, f"хаайййййййййййййййййййййЙ, {u['name']}! На счету у тя ${u['money']:,}.\n\nработа\n\n{u['name']}, выбери работу, на которой хочешь сейчас работать.\n\nтаксист", reply_markup=car_kb())

def start_taxi_trip(chat_id, user_id):
    passengers = ["Писюн", "Джек Воробей", "Мистер Кэш", "Леди Удача", "Босс", "Серёга"]
    dests = ["РОДИНА-МАТУШКА", "Аэропорт", "Казино Royale", "Пентхаус"]
    passenger = random.choice(passengers)
    dest = random.choice(dests)
    travel_time = 5
    
    msg = send_msg(chat_id, f"TAX4 TAX9 TAX1\n\n{users[user_id]['name']}, к тебе подсел {passenger}.\nВы направляетесь в город \"{dest}\" и прибудете через 1 мин 0 сек.\n\n😊 ты везёшь реального игрока и ты можешь с ним общаться — просто напиши своё сообщение в чат.\n\nКогда время выйдет, нажми на кнопку \"обновить время\", чтобы высадить пассажира.", reply_markup=trip_kb())
    
    if msg and msg.get("result"):
        active_trips[user_id] = {
            "passenger": passenger,
            "end_time": time.time() + travel_time,
            "msg_id": msg["result"]["message_id"],
            "chat_id": chat_id
        }

def finish_trip(user_id, cb_id):
    trip = active_trips.get(user_id)
    if not trip:
        send_cb(cb_id, "Нет активной поездки", True)
        return
    
    if time.time() < trip["end_time"]:
        left = int(trip["end_time"] - time.time())
        send_cb(cb_id, f"⏳ Осталось {left} сек", True)
        return
    
    u = users[user_id]
    u["money"] += 2500
    u["trips"] = u.get("trips", 0) + 1
    
    msg_text = f"✅ Поездка завершена! +$2500\n💰 Баланс: ${u['money']:,}"
    
    if not u.get("task_done") and u["trips"] >= 1:
        u["task_done"] = True
        u["money"] += 50000
        msg_text += f"\n\n🎉 Задание выполнено! +$50000\nРазблокированы другие работы и магазин одежды."
    
    send_cb(cb_id, "✅ Пассажир высажен!")
    send_msg(trip["chat_id"], msg_text, reply_markup=main_kb())
    del_msg(trip["chat_id"], trip["msg_id"])
    del active_trips[user_id]

# ========== ОБРАБОТКА CALLBACK ==========
def handle_callback(cb):
    cb_id = cb["id"]
    data = cb["data"]
    user_id = cb["from"]["id"]
    chat_id = cb["message"]["chat"]["id"]
    msg_id = cb["message"]["message_id"]
    
    # Регистрация: выбор кожи
    if data == "skin_light":
        reg_data[user_id]["skin"] = "светлый"
        edit_msg(chat_id, msg_id, "выбирай цвет кожи:\nсветлый\nтёмный\n\nя не мужик 😂\n\nтеперь причёска — выбирай:", reply_markup=hair_kb())
        reg_data[user_id]["step"] = "hair"
    elif data == "skin_dark":
        reg_data[user_id]["skin"] = "тёмный"
        edit_msg(chat_id, msg_id, "выбирай цвет кожи:\nсветлый\nтёмный\n\nя не мужик 😂\n\nтеперь причёска — выбирай:", reply_markup=hair_kb())
        reg_data[user_id]["step"] = "hair"
    elif data == "skin_uni":
        reg_data[user_id]["skin"] = "унисекс 😂"
        edit_msg(chat_id, msg_id, "выбирай цвет кожи:\nсветлый\nтёмный\n\nя не мужик 😂\n\nтеперь причёска — выбирай:", reply_markup=hair_kb())
        reg_data[user_id]["step"] = "hair"
    
    # Выбор причёски
    elif data in ["h1", "h2", "h3", "h4", "h5"]:
        hair_map = {"h1": "Классика", "h2": "Андеркат", "h3": "Дреды", "h4": "Лысый", "h5": "😎 ничего не нравится"}
        reg_data[user_id]["hair"] = hair_map[data]
        edit_msg(chat_id, msg_id, "теперь напиши, как ты хочешь, чтобы я тебя называл:", reply_markup=None)
        reg_data[user_id]["step"] = "name"
    
    # Работа таксиста
    elif data == "car_correct":
        del_msg(chat_id, msg_id)
        send_cb(cb_id, "✅ Ты выбрал свою машину!")
        send_msg(chat_id, f"Fffffffdd, ты находишься в таксопарке города \"LAS-VEGAS\".\n\n📍 транспорт — Cabbie (скорость 20 км/мин)\n🚗 поездок до завершения задания — 1\n\nотправиться в путь 🚗🚗🚗\n\nТы взял ключи от своей ласточки, на них написан номер \"TAX3\". Выбирай куда садиться, клиент уже ждёт.\n\nTAX2 TAX5 TAX3")
        start_taxi_trip(chat_id, user_id)
    elif data == "car_wrong":
        send_cb(cb_id, "❌ Не та машина!", True)
        edit_msg(chat_id, msg_id, f"бот бандит\nты выбрал не ту машину\n\n😊 ты стоял минут 10 и теребил замок чужого такси, клиент отменил заказ...\n\n{users[user_id]['name']}, ты находишься в таксопарке города \"LAS-VEGAS\".\n\n👌 транспорт — Cabbie (скорость 20 км/мин)\n👌 поездок до завершения задания — 1", reply_markup=car_kb())
    elif data == "back_work":
        del_msg(chat_id, msg_id)
        cmd_work(chat_id, user_id)
    
    # Завершение поездки
    elif data == "finish_trip":
        finish_trip(user_id, cb_id)
    
    send_cb(cb_id)

# ========== ОСНОВНОЙ ЦИКЛ ==========
def main():
    last_update = 0
    print("✅ Бот бандит запущен!")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=30&offset={last_update + 1}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode())
                
                if data.get("result"):
                    for update in data["result"]:
                        last_update = update["update_id"]
                        
                        # Обычные сообщения
                        if "message" in update:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            user_id = msg["from"]["id"]
                            text = msg.get("text", "")
                            
                            if text == "/start":
                                cmd_start(chat_id, user_id)
                            elif text == "🚕 Работа / задания":
                                cmd_work(chat_id, user_id)
                            elif text == "👤 Профиль":
                                cmd_profile(chat_id, user_id)
                            elif text == "🔄 Сбросить персонажа":
                                cmd_reset(chat_id, user_id)
                            elif user_id in reg_data and reg_data[user_id].get("step") == "name" and text.strip():
                                name = text.strip()[:30]
                                rd = reg_data[user_id]
                                users[user_id] = {
                                    "name": name,
                                    "skin": rd["skin"],
                                    "hair": rd["hair"],
                                    "money": 50000,
                                    "trips": 0,
                                    "task_done": False,
                                    "in_game": True
                                }
                                send_msg(chat_id, f"отлично, {name}, ты успешно закончил регистрацию!\n\nbot бандит — это твоя жизнь. тут можно зарабатывать деньги, зарабатывать лёгкие деньги, делать бизнес, покупать недвижимость, тачки и шмотки.\n\n👏 давай покажу тебе где тут что.\n\nпогнали")
                                send_msg(chat_id, f"здравствуй, {name}! на счету у тя $50.000.\n\nпредлагаю заработать немного денег!\n\n☝️ жми на кнопку \"задания\".", reply_markup=main_kb())
                                del reg_data[user_id]
                            elif user_id in active_trips:
                                passenger = active_trips[user_id]["passenger"]
                                send_msg(chat_id, f"💬 {passenger}: «Ха-ха, отличный разговор! Скоро приедем.»")
                            elif text:
                                send_msg(chat_id, "Используй кнопки меню", reply_markup=main_kb())
                        
                        # Callback-запросы (кнопки)
                        elif "callback_query" in update:
                            handle_callback(update["callback_query"])
        
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
