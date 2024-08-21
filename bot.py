import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database import add_course, remove_course, get_courses, add_admin, get_admins

TOKEN = '6743641196:AAHeR0_dDYD8fAXbe5mCS6_Zgqf6l4Cp-QM'
ADMIN_CHAT_ID = -1002177188908  # ID группы, куда будут отправляться заявки

bot = telebot.TeleBot(TOKEN)

# Получение списка курсов и админов из базы данных
courses = get_courses()
ADMIN_USER_IDS = get_admins()
# Хранение данных о пользователях
user_data = {}

# Хранение ID сообщений с выбором курса
course_message_ids = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("Русский язык 🇷🇺", callback_data='ru'),
        InlineKeyboardButton("O'zbek tili 🇺🇿", callback_data='uz'),
        InlineKeyboardButton("English 🇬🇧", callback_data='en')
    )
    bot.send_message(message.chat.id, "Выберите язык / Tilni tanlang / Select language:", reply_markup=markup)


# Обработчик нажатия на Inline кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ['ru', 'uz', 'en']:
        language = call.data
        user_data[call.from_user.id] = {'language': language}

        # Удаление сообщения с выбором языка
        bot.delete_message(call.message.chat.id, call.message.message_id)

        if language == 'ru':
            bot.send_message(call.message.chat.id, "Здравствуйте! Напишите ваше полное имя и фамилию.")
        elif language == 'uz':
            bot.send_message(call.message.chat.id, "Assalomu alaykum! To‘liq ismingiz va familiyangizni yozing.")
        elif language == 'en':
            bot.send_message(call.message.chat.id, "Hello! Please enter your full name.")

        bot.register_next_step_handler(call.message, get_full_name)

    elif call.data in courses:
        select_course(call)

    elif call.data.startswith('remove_'):
        course = call.data.replace('remove_', '')
        if course in courses:
            remove_course(course)  # Удаление из базы данных
            courses.remove(course)  # Удаление из списка
            bot.send_message(call.message.chat.id, f"Курс '{course}' был удален.")
        else:
            bot.send_message(call.message.chat.id, "Такого курса нет.")


# Функция для получения полного имени
def get_full_name(message):
    user_data[message.from_user.id]['name'] = message.text

    language = user_data[message.from_user.id]['language']
    if language == 'ru':
        msg = "Отправьте ваш контакт."
    elif language == 'uz':
        msg = "Kontakt raqamingizni yuboring."
    elif language == 'en':
        msg = "Please send your contact."

    contact_button = KeyboardButton(text=msg, request_contact=True)
    contact_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    contact_markup.add(contact_button)

    bot.send_message(message.chat.id, msg, reply_markup=contact_markup)
    bot.register_next_step_handler(message, get_contact)


# Функция для получения контакта
def get_contact(message):
    user_id = message.from_user.id
    if message.contact:
        phone_number = message.contact.phone_number
        user_data[user_id]['contact'] = phone_number

        language = user_data[user_id]['language']
        if language == 'ru':
            msg = "Выберите курс для регистрации."
        elif language == 'uz':
            msg = "Ro'yxatdan o'tish uchun kursni tanlang."
        elif language == 'en':
            msg = "Please select a course for registration."

        markup = InlineKeyboardMarkup()
        if not courses:
            bot.send_message(message.chat.id, "На данный момент нет доступных курсов.")
            return

        for course in courses:
            markup.add(InlineKeyboardButton(course, callback_data=course))

        # Отправка сообщения с выбором курса и сохранение его ID
        course_message = bot.send_message(message.chat.id, msg, reply_markup=markup)
        course_message_ids[message.chat.id] = course_message.message_id

    else:
        bot.send_message(user_id, "Пожалуйста, отправьте ваш контакт через кнопку.")
        contact_button = KeyboardButton(text="Отправить контакт", request_contact=True)
        contact_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        contact_markup.add(contact_button)
        bot.send_message(user_id, "Отправьте свой номер через кнопку в меню", reply_markup=contact_markup)
        bot.register_next_step_handler(message, get_contact)


# Функция для выбора курса и отправки заявки в группу
def select_course(call):
    course = call.data
    user_data[call.from_user.id]['course'] = course

    user_info = user_data[call.from_user.id]
    language = user_info['language']
    name = user_info['name']
    contact = user_info['contact']
    tg_user_name = call.from_user.username  # Имя пользователя Telegram

    # Сообщение для отправки в группу
    msg_to_group = (f"Новая заявка\n"
                    f"Имя: {name}\n"
                    f"Номер: {contact}\n"
                    f"tg_user_name: @{tg_user_name}\n"
                    f"Курс: {course}")

    bot.send_message(ADMIN_CHAT_ID, msg_to_group)

    # Сообщение с благодарностью пользователю
    if language == 'ru':
        thank_you_msg = f"{name}, спасибо за регистрацию на курс ! Мы скоро с вами свяжемся."
    elif language == 'uz':
        thank_you_msg = f"{name}, ro'yxatdan o'tganingiz uchun rahmat! Tez orada siz bilan bog'lanamiz."
    elif language == 'en':
        thank_you_msg = f"{name}, thank you for registering! We will contact you soon."

    bot.send_message(call.message.chat.id, thank_you_msg)

    # Удаление сообщения с выбором курса
    if call.message.chat.id in course_message_ids:
        bot.delete_message(call.message.chat.id, course_message_ids[call.message.chat.id])


# Админ панель для добавления и удаления курсов
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if str(message.from_user.id) in ADMIN_USER_IDS:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(
            KeyboardButton("Добавить курс"),
            KeyboardButton("Удалить курс"),
            KeyboardButton("Добавить админа")
        )
        bot.send_message(message.chat.id, "Админ панель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")


# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if str(message.from_user.id) in ADMIN_USER_IDS:
        if message.text == "Добавить курс":
            bot.send_message(message.chat.id, "Введите название курса.")
            bot.register_next_step_handler(message, add_course_handler)
        elif message.text == "Удалить курс":
            markup = InlineKeyboardMarkup()
            for course in courses:
                markup.add(InlineKeyboardButton(course, callback_data=f'remove_{course}'))
            bot.send_message(message.chat.id, "Выберите курс для удаления.", reply_markup=markup)
        elif message.text == "Добавить админа":
            bot.send_message(message.chat.id, "Введите ID нового администратора.")
            bot.register_next_step_handler(message, add_admin_handler)


def add_course_handler(message):
    course_name = message.text
    add_course(course_name)  # Добавление курса в базу данных
    courses.append(course_name)  # Добавление курса в список
    bot.send_message(message.chat.id, f"Курс '{course_name}' добавлен.")


def add_admin_handler(message):
    admin_id = message.text
    add_admin(admin_id)  # Добавление администратора в базу данных
    ADMIN_USER_IDS.append(admin_id)  # Добавление администратора в список
    bot.send_message(message.chat.id, f"Админ с ID {admin_id} добавлен.")


bot.polling(none_stop=True)
