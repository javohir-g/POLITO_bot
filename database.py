import sqlite3


# Подключение к базе данных (если файла базы данных нет, он будет создан)
def connect_db():
    return sqlite3.connect('bot_database.db')


# Создание таблиц курсов и админов
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Создание таблицы курсов
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )''')

    # Создание таблицы админов
    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        admin_id TEXT NOT NULL UNIQUE
                    )''')
    #cursor.execute("INSERT INTO admins (admin_id) VALUES (?)", (947732542,))
    conn.commit()
    conn.close()


# Добавление нового курса
def add_course(course_name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO courses (name) VALUES (?)", (course_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Курс уже существует")
    conn.close()


# Удаление курса
def remove_course(course_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE name = ?", (course_name,))
    conn.commit()
    conn.close()


# Получение всех курсов
def get_courses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM courses")
    courses = [course[0] for course in cursor.fetchall()]
    conn.close()
    return courses


# Добавление нового админа
def add_admin(admin_id):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO admins (admin_id) VALUES (?)", (admin_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Админ уже существует")
    conn.close()


# Удаление админа
def remove_admin(admin_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE admin_id = ?", (admin_id,))
    conn.commit()
    conn.close()


# Получение всех админов
def get_admins():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id FROM admins")
    admins = [admin[0] for admin in cursor.fetchall()]
    conn.close()
    return admins


# Инициализация базы данных при запуске
create_tables()
