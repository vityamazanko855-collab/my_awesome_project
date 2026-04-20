import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ========== КОНФИГ ==========
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"  # Замените на реальный токен

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== ХРАНИЛИЩЕ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ ==========
user_data = {}  # user_id -> dict

# ========== FSM СОСТОЯНИЯ ==========
class RegStates(StatesGroup):
    waiting_skin = State()
    waiting_hair = State()
    waiting_name = State()

class TaxiStates(StatesGroup):
    waiting_car_choice = State()
    in_trip = State()

# ========== КЛАВИАТУРЫ ==========
def main_menu_kb():
    kb = [
        [KeyboardButton(text="🚕 Работа / задания")],
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🔄 Сбросить персонажа")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_kb():
    kb = [[KeyboardButton(text="◀ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def get_player(user_id):
    return user_data.get(user_id, {})

def update_player(user_id, **kwargs):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id].update(kwargs)

def add_money(user_id, amount):
    if user_id in user_data:
        user_data[user_id]["money"] = user_data[user_id].get("money", 50000) + amount

# ========== ОБРАБОТЧИКИ ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get("in_game"):
        await message.answer(
            f"👋 С возвращением, {user_data[user_id]['name']}!\n"
            f"💰 Баланс: ${user_data[user_id]['money']:,}\n"
            f"📋 Задание: {'✅ выполнено' if user_data[user_id].get('task_done') else 'сделать 1 поездку таксиста'}",
            reply_markup=main_menu_kb()
        )
    else:
        await message.answer(
            "🤖 *bot бандит*\n\n"
            "Это игра прямо в Telegram.\n"
            "💰 Можно зарабатывать деньги, делать бизнес, покупать тачки и недвижку.\n\n"
            "Давай зарегистрируем твоего персонажа!",
            parse_mode="Markdown"
        )
        await message.answer("Выбери цвет кожи:", reply_markup=cancel_kb())
        await RegStates.waiting_skin.set()

@dp.message(RegStates.waiting_skin)
async def reg_skin(message: types.Message, state: FSMContext):
    skin = message.text.lower()
    if skin not in ["светлый", "тёмный", "я не мужик 😂"]:
        await message.answer("Пожалуйста, выбери один из вариантов: светлый, тёмный или 'я не мужик 😂'")
        return
    await state.update_data(skin=skin)
    await message.answer("Теперь выбери причёску (или нажми 'ничего не нравится'):",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[["Классика", "Андеркат"], ["Дреды", "Лысый"], ["ничего не нравится"]],
                             resize_keyboard=True
                         ))
    await RegStates.waiting_hair.set()

@dp.message(RegStates.waiting_hair)
async def reg_hair(message: types.Message, state: FSMContext):
    hair = message.text
    if hair not in ["Классика", "Андеркат", "Дреды", "Лысый", "ничего не нравится"]:
        await message.answer("Пожалуйста, выбери причёску из предложенных.")
        return
    if hair == "ничего не нравится":
        hair = "😎 бунтарская"
    await state.update_data(hair=hair)
    await message.answer("Отлично! Теперь напиши, как я буду тебя называть:",
                         reply_markup=cancel_kb())
    await RegStates.waiting_name.set()

@dp.message(RegStates.waiting_name)
async def reg_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name or len(name) > 30:
        await message.answer("Имя не может быть пустым или слишком длинным (макс 30 символов).")
        return
    data = await state.get_data()
    user_id = message.from_user.id
    update_player(user_id,
                  name=name,
                  skin=data['skin'],
                  hair=data['hair'],
                  money=50000,
                  task_done=False,
                  taxi_trips=0,
                  in_game=True)
    await state.clear()
    await message.answer(
        f"✨ Отлично, {name}! Регистрация завершена.\n"
        f"🎨 Кожа: {data['skin']}\n💇 Причёска: {data['hair']}\n"
        f"💰 Стартовый капитал: $50,000\n\n"
        f"📌 Твоё первое задание: **сделать 1 поездку на такси**\n"
        f"Используй кнопку '🚕 Работа / задания'",
        reply_markup=main_menu_kb(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "👤 Мой профиль")
async def profile(message: types.Message):
    user_id = message.from_user.id
    p = get_player(user_id)
    if not p.get("in_game"):
        await message.answer("Ты ещё не зарегистрирован. Напиши /start")
        return
    await message.answer(
        f"👤 *{p['name']}*\n"
        f"🎨 Кожа: {p['skin']}\n💇 Причёска: {p['hair']}\n"
        f"💰 Деньги: ${p['money']:,}\n"
        f"🚕 Поездок таксистом: {p.get('taxi_trips', 0)}\n"
        f"📋 Задание: {'✅ выполнено' if p.get('task_done') else 'сделать 1 поездку таксиста'}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

@dp.message(F.text == "🚕 Работа / задания")
async def work_menu(message: types.Message):
    user_id = message.from_user.id
    p = get_player(user_id)
    if not p.get("in_game"):
        await message.answer("Сначала зарегистрируйся: /start")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚕 Таксист", callback_data="job_taxi")],
        [InlineKeyboardButton(text="🏭 Бизнесмен (скоро)", callback_data="job_business")],
        [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_main")]
    ])
    await message.answer("Выбери работу:", reply_markup=kb)

@dp.callback_query(F.data == "job_taxi")
async def taxi_job_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    p = get_player(user_id)
    if not p.get("in_game"):
        await callback.answer("Зарегистрируйся через /start")
        return
    await callback.message.delete()
    await callback.message.answer(
        "🚕 *Таксопарк LAS-VEGAS*\n"
        "Твой автомобиль: Cabbie (20 км/мин)\n"
        f"Поездок до выполнения задания: {0 if p.get('task_done') else 1}\n\n"
        "Выбери машину:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="TAX2", callback_data="car_wrong"),
             InlineKeyboardButton(text="TAX5", callback_data="car_wrong"),
             InlineKeyboardButton(text="TAX3 (твоя)", callback_data="car_correct")],
            [InlineKeyboardButton(text="TAX4", callback_data="car_wrong"),
             InlineKeyboardButton(text="TAX9", callback_data="car_wrong"),
             InlineKeyboardButton(text="TAX1", callback_data="car_wrong")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="back_to_work")]
        ])
    )
    await TaxiStates.waiting_car_choice.set()

@dp.callback_query(F.data == "car_wrong", StateFilter(TaxiStates.waiting_car_choice))
async def wrong_car(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("❌ Не та машина!")
    await callback.message.answer("😵 Ты теребил замок чужого такси, клиент уехал. Попробуй ещё раз.")
    await callback.message.delete()
    # повторно показать выбор
    await taxi_job_start(callback, state)

@dp.callback_query(F.data == "car_correct", StateFilter(TaxiStates.waiting_car_choice))
async def correct_car(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("✅ Ты взял ключи от своей ласточки")
    await callback.message.delete()
    # запускаем поездку
    await start_trip(callback.message, state)

async def start_trip(message: types.Message, state: FSMContext):
    passengers = ["Писюн", "Джек Воробей", "Мистер Кэш", "Леди Удача", "Босс", "Серёга"]
    destinations = ["РОДИНА-МАТУШКА", "Аэропорт", "Казино Royale", "Пентхаус", "Полицейский участок", "Пляж"]
    passenger = random.choice(passengers)
    destination = random.choice(destinations)
    travel_time = 5  # секунд (в реальном боте можно сделать 60, но для теста 5)

    await state.update_data(passenger=passenger, destination=destination, end_time=asyncio.get_event_loop().time() + travel_time)
    await message.answer(
        f"🚕 К тебе подсел *{passenger}*.\n"
        f"Едем в город *{destination}*. Прибудем через {travel_time} сек.\n"
        "Ты можешь общаться с пассажиром через чат.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Обновить время / высадить", callback_data="finish_trip")]
        ])
    )
    await TaxiStates.in_trip.set()

@dp.callback_query(F.data == "finish_trip", StateFilter(TaxiStates.in_trip))
async def finish_trip(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    now = asyncio.get_event_loop().time()
    if now < data.get('end_time', 0):
        remaining = int(data['end_time'] - now)
        await callback.answer(f"⏳ Ещё {remaining} сек. Подождите!")
        return

    # Поездка завершена
    earnings = 2500
    add_money(user_id, earnings)
    p = get_player(user_id)
    # Обновляем прогресс задания
    trips = p.get("taxi_trips", 0) + 1
    update_player(user_id, taxi_trips=trips, money=p["money"] + earnings)

    task_completed = False
    if not p.get("task_done") and trips >= 1:
        update_player(user_id, task_done=True)
        add_money(user_id, 50000)
        task_completed = True
        await callback.message.answer(
            f"🎉 *Задание выполнено!*\n"
            f"+$50,000 за задание\n"
            f"Тебе открыты другие работы и магазин одежды.",
            parse_mode="Markdown"
        )

    await callback.message.answer(
        f"✅ Вы высадили пассажира *{data['passenger']}*.\n"
        f"💰 Заработано: ${earnings:,}\n"
        f"💵 Баланс: ${get_player(user_id)['money']:,}\n"
        f"🚕 Всего поездок: {trips}",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )
    await state.clear()

@dp.callback_query(F.data == "back_to_work")
async def back_to_work(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await work_menu(callback.message)

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Главное меню", reply_markup=main_menu_kb())

@dp.message(F.text == "🔄 Сбросить персонажа")
async def reset_character(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    await message.answer("Персонаж сброшен. Напиши /start, чтобы создать нового.", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text == "◀ Отмена")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb())

@dp.message()
async def chat_with_passenger(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state == TaxiStates.in_trip:
        data = await state.get_data()
        await message.answer(f"💬 *{data.get('passenger', 'Пассажир')}*: «Ха-ха, отличный разговор! Скоро приедем.»", parse_mode="Markdown")
    else:
        await message.answer("Используй кнопки меню.", reply_markup=main_menu_kb())

# ========== ЗАПУСК ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
