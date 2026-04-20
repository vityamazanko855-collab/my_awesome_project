import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

TOKEN = "8655886367:AAGQMnYq2OEGI50vn2Z1TWe1P--zp-zydr0"

CHOOSING_NICK = 1
user_data_dict = {}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_city_keyboard():
    keyboard = [
        [KeyboardButton("🏙️ город"), KeyboardButton("👤 профиль"), KeyboardButton("📈 топ")],
        [KeyboardButton("🏪 бизнес"), KeyboardButton("💼 работа"), KeyboardButton("🏦 вклад")],
        [KeyboardButton("💰 казино"), KeyboardButton("🎰 игры"), KeyboardButton("📦 кейсы")],
        [KeyboardButton("📬 биржа"), KeyboardButton("⚔️ кланы"), KeyboardButton("📊 статистика")],
        [KeyboardButton("📱 привязать"), KeyboardButton("💳 карта"), KeyboardButton("🔄 обмен")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_work_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 рефка", callback_data='work_ref')],
        [InlineKeyboardButton("🏢 бизнес", callback_data='work_biz')],
        [InlineKeyboardButton("🔫 блок", callback_data='work_block')],
        [InlineKeyboardButton("🚕 таксист", callback_data='work_taxi')],
        [InlineKeyboardButton("👮 федерал", callback_data='work_fed')],
        [InlineKeyboardButton("🔙 вернуться в главное меню", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = user.id

    if user_id in user_data_dict and "nick" in user_data_dict[user_id]:
        await send_welcome_message(update, context, user_data_dict[user_id]["nick"])
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "🎲 *бот бандит*\n\n"
            "Чтобы начать игру, нужно зарегистрироваться.\n"
            "Придумай и напиши свой *никнейм*:",
            parse_mode='Markdown'
        )
        return CHOOSING_NICK

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, nick: str):
    text = (
        f"💡 *используй кнопки! чтобы переместиться в главное меню используй команду /m*\n\n"
        f"и снова привет, *{nick}*! сейчас ты находишься в городе \"LAS-VEGAS\". на счету у тя $0.\n\n"
        f"*{nick}*, выбери работу, на которой хочешь сейчас работать.\n\n"
        f"📋 *Сообщение*"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_work_keyboard())
    await update.message.reply_text("🏙️ *LAS-VEGAS* | 💰 $0", parse_mode='Markdown', reply_markup=get_city_keyboard())

async def nickname_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    nick = update.message.text.strip()
    if not nick:
        await update.message.reply_text("Никнейм не может быть пустым. Попробуй ещё раз:")
        return CHOOSING_NICK
    user_data_dict[user_id] = {"nick": nick, "balance": 0}
    await send_welcome_message(update, context, nick)
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if query.data == 'main_menu':
        if user_id in user_data_dict:
            await query.edit_message_text(
                f"💡 *используй кнопки! чтобы переместиться в главное меню используй команду /m*\n\n"
                f"и снова привет, *{user_data_dict[user_id]['nick']}*! сейчас ты находишься в городе \"LAS-VEGAS\". на счету у тя $0.\n\n"
                f"*{user_data_dict[user_id]['nick']}*, выбери работу, на которой хочешь сейчас работать.\n\n"
                f"📋 *Сообщение*",
                parse_mode='Markdown',
                reply_markup=get_work_keyboard()
            )
        else:
            await query.edit_message_text("Сначала зарегистрируйтесь через /start")
        return
    work_messages = {
        'work_ref': "📢 Ты выбрал работу рефка. Функция в разработке.",
        'work_biz': "🏢 Ты выбрал работу бизнес. Функция в разработке.",
        'work_block': "🔫 Ты выбрал работу блок. Функция в разработке.",
        'work_taxi': "🚕 Ты выбрал работу таксист. Функция в разработке.",
        'work_fed': "👮 Ты выбрал работу федерал. Функция в разработке.",
    }
    await query.edit_message_text(
        work_messages.get(query.data, "Неизвестная команда"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data='main_menu')]])
    )

async def main_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in user_data_dict:
        await update.message.reply_text(
            f"💡 *используй кнопки! чтобы переместиться в главное меню используй команду /m*\n\n"
            f"и снова привет, *{user_data_dict[user_id]['nick']}*! сейчас ты находишься в городе \"LAS-VEGAS\". на счету у тя $0.\n\n"
            f"*{user_data_dict[user_id]['nick']}*, выбери работу, на которой хочешь сейчас работать.\n\n"
            f"📋 *Сообщение*",
            parse_mode='Markdown',
            reply_markup=get_work_keyboard()
        )

def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={CHOOSING_NICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, nickname_received)]},
        fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('m', main_menu_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
