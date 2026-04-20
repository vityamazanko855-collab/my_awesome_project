import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# ========== КОНФИГ ==========
BOT_TOKEN = "8655886367:AAGQMnYq2OEGI50vn2Z1TWe1P--zp-zydr0"  # ВСТАВЬ СВОЙ ТОКЕН

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== ДАННЫЕ ПОЛЬЗОВАТЕЛЕЙ ==========
user_data = {}  # {user_id: {"nick": "Fffffsd", "balance": 50000, "trips_done": 0, "reg_complete": False}}

# ========== КЛАВИАТУРЫ ==========
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Меню"), KeyboardButton(text="Сообщение")]],
    resize_keyboard=True
)

yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✔ создать человечка")]],
    resize_keyboard=True
)

skin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="светлый"), KeyboardButton(text="тёмный")],
              [KeyboardButton(text="я не мужик 😂")]],
    resize_keyboard=True
)

hair_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="ничего не нравится")]],
    resize_keyboard=True
)

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="☰ жми на кнопку \"задания\"")]],
    resize_keyboard=True
)

work_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="таксист")],
              [KeyboardButton(text="вернуться в главное меню")]],
    resize_keyboard=True
)

taxi_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="отправиться в путь 🚗🚙")],
              [KeyboardButton(text="назад"), KeyboardButton(text="подробнее")]],
    resize_keyboard=True
)

car_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="TAX2"), KeyboardButton(text="TAX5"), KeyboardButton(text="TAX3")],
              [KeyboardButton(text="назад")]],
    resize_keyboard=True
)

update_time_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="обновить время")]],
    resize_keyboard=True
)

# ========== FSM СОСТОЯНИЯ ==========
class RegStates(StatesGroup):
    waiting_for_nick = State()
    waiting_for_skin = State()
    waiting_for_hair = State()

class GameStates(StatesGroup):
    waiting_for_work = State()
    waiting_for_taxi_start = State()
    waiting_for_car_choice = State()
    waiting_for_trip = State()

# ========== РАНДОМНЫЕ ПАССАЖИРЫ ==========
passenger_names = ["Писюн", "Кек", "Баклажан", "Сосиска", "Чебурек", 
                   "Мотя", "Шуруп", "Батон", "Лысый", "Кукуся"]

# ========== КОМАНДА СТАРТ ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id in user_data and user_data[user_id].get("reg_complete", False):
        # Уже зареган
        await show_main_menu(message, user_id)
    else:
        # Начинаем регистрацию
        user_data[user_id] = {"reg_complete": False}
        await message.answer(
            "регистрация\n\n"
            "привет, , вижу у тебя ещё нет человечка в бот бандите!\n\n"
            "давай это исправим.",
            reply_markup=yes_no_keyboard
        )
        await state.set_state(RegStates.waiting_for_skin)

# ========== РЕГИСТРАЦИЯ: ВЫБОР КОЖИ ==========
@dp.message(RegStates.waiting_for_skin, F.text == "✔ создать человечка")
async def reg_skin(message: types.Message, state: FSMContext):
    await message.answer(
        "выбирай цвет кожи:\n\n"
        "светлый\n"
        "тёмный\n"
        "я не мужик 😂",
        reply_markup=skin_keyboard
    )
    await state.set_state(RegStates.waiting_for_hair)

# ========== РЕГИСТРАЦИЯ: ПРИЧЕСКА ==========
@dp.message(RegStates.waiting_for_hair, F.text.in_(["светлый", "тёмный", "я не мужик 😂"]))
async def reg_hair(message: types.Message, state: FSMContext):
    await state.update_data(skin=message.text)
    await message.answer(
        "теперь причёска — выбирай:",
        reply_markup=hair_keyboard
    )
    await state.set_state(RegStates.waiting_for_nick)

# ========== РЕГИСТРАЦИЯ: НИКНЕЙМ ==========
@dp.message(RegStates.waiting_for_nick, F.text == "ничего не нравится")
async def reg_nick(message: types.Message, state: FSMContext):
    await message.answer(
        "теперь напиши, как ты хочешь, чтобы я тебя называл:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegStates.waiting_for_nick)

@dp.message(RegStates.waiting_for_nick)
async def reg_save_nick(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    nick = message.text.strip()
    
    if len(nick) > 20:
        await message.answer("Слишком длинное имя, попробуй короче:")
        return
    
    user_data[user_id] = {
        "nick": nick,
        "balance": 50000,
        "trips_done": 0,
        "reg_complete": True
    }
    
    await message.answer(
        f"отлично, {nick}, ты успешно закончил регистрацию!\n\n"
        f"бот бандит — это твоя жизнь. тут можно зарабатывать деньги, зарабатывать лёгкие деньги, "
        f"делать бизнес, покупать недвижимость, тачки и шмотки.\n\n"
        f"😂 давай покажу тебе где тут что.\n\n"
        f"погнали",
        reply_markup=main_menu_keyboard
    )
    await state.clear()
    await show_main_menu(message, user_id)

# ========== ГЛАВНОЕ МЕНЮ ==========
async def show_main_menu(message: types.Message, user_id: int):
    user = user_data.get(user_id, {})
    nick = user.get("nick", "игрок")
    balance = user.get("balance", 0)
    
    await message.answer(
        f"здравствуй, {nick}! на счету у тя\n"
        f"${balance:,}".replace(",", "."),
        reply_markup=main_menu_keyboard
    )

@dp.message(F.text == "☰ жми на кнопку \"задания\"")
async def show_tasks(message: types.Message):
    await message.answer(
        "- текущее задание:\n\n"
        "- сделать 1 поездку на работе таксиста.\n\n"
        "- награда:\n\n"
        "- разблокировка других работ;\n"
        "- разблокировка магазина одежды;\n"
        "- $50.000.\n\n"
        "- работу таксиста можно найти в главном /menu → работа → таксист"
    )

@dp.message(F.text == "Меню")
async def menu_button(message: types.Message):
    user_id = message.from_user.id
    await show_main_menu(message, user_id)

# ========== РАБОТА ==========
@dp.message(F.text == "вернуться в главное меню")
async def back_to_menu(message: types.Message):
    user_id = message.from_user.id
    await show_main_menu(message, user_id)

@dp.message(F.text == "работа")
async def show_work(message: types.Message):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    nick = user.get("nick", "игрок")
    balance = user.get("balance", 0)
    
    await message.answer(
        f"вернуться в главное меню\n\n"
        f"ky, {nick}! на счету у тя ${balance:,}".replace(",", "."),
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        f"работа\n\n"
        f"{nick}, выбери работу, на которой хочешь сейчас работать.",
        reply_markup=work_keyboard
    )

@dp.message(F.text == "таксист")
async def taxi_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = user_data.get(user_id, {})
    nick = user.get("nick", "игрок")
    trips_done = user.get("trips_done", 0)
    required = 1 - trips_done
    
    await message.answer(
        f"Таксист\n\n"
        f"{nick}, ты находишься в таксопарке города \"LAS-VEGAS\".\n\n"
        f"транспорт — Cabbie (скорость 20 км/мин)\n"
        f"поездок до завершения задания — {required}",
        reply_markup=taxi_keyboard
    )
    await state.set_state(GameStates.waiting_for_taxi_start)

@dp.message(GameStates.waiting_for_taxi_start, F.text == "отправиться в путь 🚗🚙")
async def taxi_choose_car(message: types.Message, state: FSMContext):
    await message.answer(
        "отправиться в путь\n\n"
        "ты взял ключи от своей ласточки,\n"
        "на них написан номер \"ТАХ3\". выбирай\n"
        "куда садиться, клиент уже ждёт.",
        reply_markup=car_choice_keyboard
    )
    await state.set_state(GameStates.waiting_for_car_choice)

# ========== ПРОВЕРКА МАШИНЫ ==========
@dp.message(GameStates.waiting_for_car_choice, F.text == "назад")
async def back_to_taxi(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    nick = user_data.get(user_id, {}).get("nick", "игрок")
    trips_done = user_data.get(user_id, {}).get("trips_done", 0)
    required = 1 - trips_done
    
    await message.answer(
        f"Таксист\n\n"
        f"{nick}, ты находишься в таксопарке города \"LAS-VEGAS\".\n\n"
        f"транспорт — Cabbie (скорость 20 км/мин)\n"
        f"поездок до завершения задания — {required}",
        reply_markup=taxi_keyboard
    )
    await state.set_state(GameStates.waiting_for_taxi_start)

@dp.message(GameStates.waiting_for_car_choice, F.text.in_(["TAX2", "TAX5"]))
async def taxi_wrong_car(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    nick = user_data.get(user_id, {}).get("nick", "игрок")
    trips_done = user_data.get(user_id, {}).get("trips_done", 0)
    required = 1 - trips_done
    
    await message.answer(
        f"ты выбрал не ту машину.\n\n"
        f"ты стоял минут 10 и теребил замок чужого такси, клиент отменил заказ...\n\n"
        f"{nick}, ты находишься в таксопарке города \"LAS-VEGAS\".\n\n"
        f"транспорт — Cabbie (скорость 20 км/мин)\n"
        f"поездок до завершения задания — {required}",
        reply_markup=taxi_keyboard
    )
    await state.set_state(GameStates.waiting_for_taxi_start)

@dp.message(GameStates.waiting_for_car_choice, F.text == "TAX3")
async def taxi_right_car(message: types.Message, state: FSMContext):
    await message.answer(
        "ты сел в своё такси ТАХ3 и завёл двигатель.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Рандомный пассажир
    passenger = random.choice(passenger_names)
    await state.update_data(passenger=passenger)
    
    await message.answer(
        f"{user_data[message.from_user.id]['nick']}, к тебе подсел {passenger}.\n"
        f"вы направляетесь в город\n"
        f"\"РОДИНА-МАТУШКА\" и прибудете\n"
        f"через 1 мин 0 сек.\n\n"
        f"💬 ты везёшь реального игрока и ты\n"
        f"можешь с ним общаться — просто\n"
        f"напиши своё сообщение в чат.\n\n"
        f"📌 когда время выйдет, нажми на\n"
        f"кнопку \"обновить время\", чтобы\n"
        f"высадить пассажира.",
        reply_markup=update_time_keyboard
    )
    await state.set_state(GameStates.waiting_for_trip)

# ========== ЗАВЕРШЕНИЕ ПОЕЗДКИ ==========
@dp.message(GameStates.waiting_for_trip, F.text == "обновить время")
async def finish_trip(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    passenger = data.get("passenger", "пассажир")
    
    # Обновляем данные
    user_data[user_id]["balance"] += 50000
    user_data[user_id]["trips_done"] = 1
    
    nick = user_data[user_id]["nick"]
    new_balance = user_data[user_id]["balance"]
    
    await message.answer(
        f"ты высадил {passenger}.\n"
        f"Поездка завершена.\n\n"
        f"✅ задание выполнено!\n"
        f"+$50.000\n"
        f"Разблокированы другие работы и магазин одежды.\n\n"
        f"Твой баланс: ${new_balance:,}".replace(",", "."),
        reply_markup=main_menu_keyboard
    )
    await state.clear()

# ========== ЗАПУСК ==========
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
