import json
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Файл для хранения данных
DATA_FILE = 'users_data.json'

# Загрузка данных из JSON
def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Сохранение данных в JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Команда /start
def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    users = load_data()

    if user_id not in users:
        users[user_id] = {
            'username': update.message.from_user.username,
            'balance': 1000
        }
        save_data(users)

    keyboard = [
        [InlineKeyboardButton("Профиль", callback_data='profile')],
        [InlineKeyboardButton("Трейд", callback_data='trade')],
        [InlineKeyboardButton("Ежедневный бонус", callback_data='bonus')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

# Профиль
def profile(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = str(query.from_user.id)
    users = load_data()

    username = users[user_id]['username']
    balance = users[user_id]['balance']

    query.edit_message_text(f"Ваш профиль:\n\nНикнейм: {username}\nБаланс: {balance} монет")

# Трейд
def trade(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("Вверх", callback_data='up')],
        [InlineKeyboardButton("Вниз", callback_data='down')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text("Выберите, куда пойдёт курс:\n\n1. Вверх\n2. Вниз", reply_markup=reply_markup)

# Процесс трейда
def process_trade(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = str(query.from_user.id)
    users = load_data()
    balance = users[user_id]['balance']

    # Генерация случайного направления курса
    real_direction = random.choice(['up', 'down'])
    bet_direction = query.data

    if balance <= 0:
        query.edit_message_text("У вас недостаточно средств для ставки.")
        return

    # Запрашиваем ставку
    query.edit_message_text("Введите размер ставки:")
    context.user_data['bet_direction'] = bet_direction
    context.user_data['real_direction'] = real_direction

# Обработка ставки
def handle_bet(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    bet_amount = int(update.message.text)
    users = load_data()

    balance = users[user_id]['balance']
    bet_direction = context.user_data['bet_direction']
    real_direction = context.user_data['real_direction']

    if bet_amount > balance:
        update.message.reply_text("У вас недостаточно средств для этой ставки.")
        return

    # Если угадал направление, баланс удваивается
    if bet_direction == real_direction:
        balance += bet_amount
        update.message.reply_text(f"Вы угадали! Баланс увеличен: {balance} монет.")
    else:
        balance -= bet_amount
        update.message.reply_text(f"Вы не угадали. Текущий баланс: {balance} монет.")

    users[user_id]['balance'] = balance
    save_data(users)

# Ежедневный бонус
def daily_bonus(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = str(query.from_user.id)
    users = load_data()

    users[user_id]['balance'] += 100
    save_data(users)

    query.edit_message_text("Вы получили 100 монет! Ваш баланс обновлён.")

# Обработка кнопок
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'profile':
        profile(update, context)
    elif query.data == 'trade':
        trade(update, context)
    elif query.data == 'bonus':
        daily_bonus(update, context)
    elif query.data in ['up', 'down']:
        process_trade(update, context)

# Основная функция запуска бота
def main():
    # Замените токен на свой от BotFather
    TOKEN = "7288195056:AAH7m4eA-yrlwBF5fi-JYLZ-sIwreY6qVZo"

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_bet))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
