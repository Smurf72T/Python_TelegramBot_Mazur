# init_db.py — полный скрипт инициализации/обновления таблиц
# Запускать один раз после изменений в моделях

import psycopg2
import time
from db_config import DB_CONFIG

# Ожидание готовности базы данных
def wait_for_db():
    """Ожидание готовности базы данных перед подключением"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                connect_timeout=5
            )
            conn.close()
            print(f"База данных доступна после {attempt + 1} попыток")
            break
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                print(f"Не удалось подключиться к базе данных после {max_retries} попыток: {e}")
                raise
            print(f"Попытка {attempt + 1}/{max_retries}: База данных не готова, ждем {retry_delay} сек...")
            time.sleep(retry_delay)

print("Ожидание готовности базы данных...")
wait_for_db()

conn = psycopg2.connect(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["database"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"]
)
conn.autocommit = True
cur = conn.cursor()

print("Подключение к базе данных установлено.")

# 1. Таблица users — с ВСЕМИ полями из модели UserProfile
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id     BIGINT PRIMARY KEY,
    username        TEXT,
    first_name      TEXT,
    last_name       TEXT,
    email           TEXT,
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    export_token    TEXT UNIQUE
);
""")

# Добавляем/обновляем поля, если их нет
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS export_token TEXT UNIQUE;")

# 2. Таблица events — с user_id как FK
cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    event_date  DATE NOT NULL,
    event_time  TIME NOT NULL,
    details     TEXT DEFAULT '',
    is_public   BOOLEAN DEFAULT FALSE
);
""")

# 3. Таблица appointments
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id                      SERIAL PRIMARY KEY,
    organizer_id            BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    event_id                INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    participant_telegram_id BIGINT NOT NULL,
    date                    DATE NOT NULL,
    time                    TIME NOT NULL,
    details                 TEXT DEFAULT '',
    status                  TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'declined', 'cancelled')),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, participant_telegram_id)
);
""")

# 4. Таблица bot_statistics
cur.execute("""
CREATE TABLE IF NOT EXISTS bot_statistics (
    date             DATE PRIMARY KEY,
    user_count       INTEGER DEFAULT 0,
    event_count      INTEGER DEFAULT 0,
    edited_events    INTEGER DEFAULT 0,
    cancelled_events INTEGER DEFAULT 0
);
""")

# 5. Таблица user_statistics — с правильным именем поля user_telegram_id
cur.execute("""
CREATE TABLE IF NOT EXISTS user_statistics (
    user_telegram_id    BIGINT PRIMARY KEY REFERENCES users(telegram_id) ON DELETE CASCADE,
    created_events      INTEGER DEFAULT 0,
    edited_events       INTEGER DEFAULT 0,
    cancelled_events    INTEGER DEFAULT 0,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.close()
conn.close()

print("Все таблицы и поля созданы или обновлены.")
print("Теперь можно запускать бота и Django-админку без ошибок.")
print("Рекомендация: перезапустите Django-сервер и бота после выполнения.")