import logging
import sqlite3
from datetime import datetime
from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

API_TOKEN = 'API_TOKEN'
logging.basicConfig(level=logging.INFO)

x = False
admins = [""]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Устанавливаем соединение с базой данных SQLite
conn = sqlite3.connect('chat_ids.db')
cursor = conn.cursor()

# Создаем таблицу для хранения chat_id, если она еще не существует
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_ids
                  (chat_id INTEGER PRIMARY KEY)''')

conn.commit()

y = False


# Обработка команды /start_listening


@dp.message_handler(commands=['start_listening'])
async def start_listening_command(message: types.Message):
    add_chat_to_database(message.chat.id)
    # Отправляем сообщение "начинаю слушать"
    # Удаляем сообщение с командой для всех участников чата
    await bot.delete_message(message.chat.id, message.message_id)


# Ожидаем сообщение от пользователя
@dp.message_handler(Command("add_admin"))
async def process_broadcast_command(message: types.Message):
    global y
    global admins
    if (message.from_user.username in admins):
        y = True
        await message.reply(
            "Ответьте на это сообщение, написав ник пользователя в телеграмме, которого нужно добавить в администраторы бота. \n\nВведите ник в формате: nickname \nБЕЗ ЗНАЧКА @")
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


# Обработка ответа на сообщение для рассылки


@dp.message_handler(lambda message: message.reply_to_message and message.reply_to_message.text ==
                                    "Ответьте на это сообщение, написав ник пользователя в телеграмме, которого нужно добавить в администраторы бота. \n\nВведите ник в формате: nickname \nБЕЗ ЗНАЧКА @")
async def process_message_for_broadcast(msg: types.Message):
    global y

    if (y and msg.text not in admins):
        new_admin = msg.text  # Сохраняем сообщение в переменной типа string
        admins.append(new_admin)
        await bot.send_message(msg.chat.id,
                               f"Пользователь с ником: {new_admin} успешно добавлен в администраторы бота.")
        y = False
    elif (msg.text in admins):
        await bot.send_message(msg.chat.id, f"Пользователь с ником: {msg.text} уже является администратором бота.")
    else:
        await bot.send_message(msg.chat.id,
                               "Для добавление пользователя в администраторы бота воспользуйтесь командой /add_admin")
        y = False


# Ожидаем сообщение от пользователя


@dp.message_handler(Command("help"))
async def process_broadcast_command(message: types.Message):
    CHAT_ID = message.chat.id

    global x
    global admins
    if (message.from_user.username in admins):
        await message.reply(
            "/help - просмотр всех команд\n/send_to_all - отправить рассылку всем чатам\n/add_admin - добавить администратора бота\n/start - запустить привественное сообщение\n/start_listening - активация бота для чатов с клиентами")
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


# Функция для добавления chat_id в базу данных


def add_chat_to_database(chat_id):
    conn = sqlite3.connect('chat_ids.db')
    c = conn.cursor()

    # Проверяем, существует ли уже такой chat_id в базе данных
    c.execute("SELECT * FROM chat_ids WHERE chat_id = ?", (chat_id,))
    existing_chat = c.fetchone()

    if not existing_chat:
        # Если chat_id не найден, то добавляем его в базу данных
        c.execute("INSERT INTO chat_ids (chat_id) VALUES (?)", (chat_id,))
        conn.commit()

    conn.close()


#    conn = sqlite3.connect('chat_ids.db')  # Подключаемся к базе данных
#    c = conn.cursor()
#    c.execute("INSERT INTO chat_ids (chat_id) VALUES (?)",
#              (chat_id,))  # Добавляем chat_id в таблицу
#    conn.commit()  # Сохраняем изменения
#    conn.close()  # Закрываем соединение

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def greet_new_members(message: types.Message):
    add_chat_to_database(message.chat.id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_yes = KeyboardButton("Да 🐶")
    keyboard.add(button_yes)

    new_members = message.new_chat_members
    for member in new_members:
        # Повторно проверяем, является ли новый пользователь администратором (это может быть избыточным, но добавлено для уверенности)
        if member.username in admins:
            continue

        # Отправляем приветственное сообщение только для обычных пользователей
        await bot.send_message(message.chat.id,
                               f"{member.mention} \n{member.first_name}, дорогой родитель собаки, добро пожаловать в рабочий чат Школы доброй кинологии! "
                               "\n \nЗдесь Вы сможете задать вопросы касательно обучения и уточнить организационные моменты. "
                               "Также здесь мы будем выкладывать домашнее задание, полезные советы, отвечать на ваши вопросы, "
                               "а вы — присылать видеозаписи выполненных упражнений после консультации✌️ \n \nГотовы начать "
                               "подготовку к занятиям?", reply_markup=keyboard)


@dp.message_handler(Command("start"))
async def start(message: types.Message):
    # Сохраняем chat_id в базу данных SQLite
    chat_id = message.chat.id
    cursor.execute(
        'INSERT OR IGNORE INTO chat_ids (chat_id) VALUES (?)', (chat_id,))
    conn.commit()

    # Отправляем приветственное сообщение с кнопкой "ДА"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_yes = KeyboardButton("Да 🐶")
    keyboard.add(button_yes)

    await message.answer("Дорогой родитель собаки, добро пожаловать в рабочий чат Школы доброй кинологии! "
                         "\n \nЗдесь Вы сможете задать вопросы касательно обучения и уточнить организационные моменты. "
                         "Также здесь мы будем выкладывать домашнее задание, полезные советы, отвечать на ваши вопросы, "
                         "а вы — присылать видеозаписи выполненных упражнений после консультации✌️ \n \nГотовы начать "
                         "подготовку к занятиям?", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Да 🐶")
async def ask_online(message: types.Message):
    # Отправляем новое сообщение с кнопками "ОНЛАЙН" и "ОФЛАЙН"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_online = KeyboardButton("Очная 👥")
    button_offline = KeyboardButton("Онлайн 👨‍💻")
    keyboard.add(button_online, button_offline)

    await message.answer("Выберите, пожалуйста, на какую консультацию вы записаны: очная/онлайн?",
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Очная 👥")
async def ask_online(message: types.Message):
    # Отправляем изображение по URL в ответ на сообщение "Очная"
    await bot.send_photo(message.chat.id, photo="https://ibb.co/4W7h1yK", reply_markup=ReplyKeyboardRemove())
    await bot.send_message(message.chat.id,
                           "Напишите пожалуйста все вопросы о вашем питомце, которые интересуют вас и опишите поведение, которое вас беспокоит.\n\nЭто необходимо для того чтобы занятие прошло максимально продуктивно и вы ничего не забыли уточнить. \n\nПополнять список вопросов можно до тех пор, пока они не закончатся в течение нескольких дней.")


@dp.message_handler(lambda message: message.text == "Онлайн 👨‍💻")
async def ask_online(message: types.Message):
    await bot.send_photo(message.chat.id, photo="https://ibb.co/q1nYGMf", reply_markup=ReplyKeyboardRemove())
    await bot.send_message(message.chat.id,
                           "Напишите пожалуйста все вопросы о вашем питомце, которые интересуют вас и опишите поведение, которое вас беспокоит.\n\nЭто необходимо для того чтобы занятие прошло максимально продуктивно и вы ничего не забыли уточнить. \n\nПополнять список вопросов можно до тех пор, пока они не закончатся в течение нескольких дней.")


# Ожидаем сообщение от пользователя


@dp.message_handler(Command("send_to_all"))
async def process_broadcast_command(message: types.Message):
    global x
    global admins
    if (message.from_user.username in admins):
        x = True
        await message.reply(
            "Чтобы начать рассылку, ответьте на это сообщение с текстом для рассылки. \nВНИМАНИЕ! сообщение будет отправлено ВСЕМ чатам, в которых присутсвует бот\n\nДля отмены ответьте написав: 1")
    else:
        await message.reply("У вас нет прав для выполнения этой команды.")


# Обработка ответа на сообщение для рассылки


@dp.message_handler(
    lambda message: message.reply_to_message and message.reply_to_message.text == "Чтобы начать рассылку, ответьте на это сообщение с текстом для рассылки. \nВНИМАНИЕ! сообщение будет отправлено ВСЕМ чатам, в которых присутсвует бот\n\nДля отмены ответьте написав: 1",
    content_types=['photo', 'text'])
async def process_message_for_broadcast(msg: types.Message):
    global x

    if (x and msg.photo):
        photo = msg.photo[-1]
        file_id = photo.file_id
        cursor.execute('SELECT chat_id FROM chat_ids')
        rows = cursor.fetchall()

        for row in rows:
            chatid = row[0]
            await bot.send_photo(chatid, file_id, caption=msg.caption)

        await bot.send_message(msg.chat.id, "Рассылка успешно завершена.")
        x = False
    elif (x and msg.text != "1"):
        message_to_broadcast = msg.text  # Сохраняем сообщение в переменной типа string
        cursor.execute('SELECT chat_id FROM chat_ids')
        rows = cursor.fetchall()
        for row in rows:
            chatid = row[0]
            try:
                await bot.send_message(chatid, message_to_broadcast)
            except Exception as e:
                continue
        await bot.send_message(msg.chat.id, "Рассылка успешно завершена.")
        x = False
    elif (msg.text == "1"):
        await bot.send_message(msg.chat.id, "Отмена рассылки.")
        x = False
    else:
        await bot.send_message(msg.chat.id, "Для начала рассылки воспользуйтесь командой /send_to_all")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
