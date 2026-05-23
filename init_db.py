"""
init_db.py — скрипт инициализации/обновления структуры базы данных

Назначение:
- Создает все необходимые таблицы в базе данных PostgreSQL
- Обновляет структуру существующих таблиц при изменении моделей
- Обеспечивает целостность данных через внешние ключи и ограничения

Использование:
- Запускать один раз после изменений в моделях Django
- Запускать при первоначальной настройке проекта
- Запускать при миграции базы данных

Зависимости:
- psycopg2: драйвер PostgreSQL для Python
- python-dotenv: загрузка переменных окружения из .env
"""

import os
import psycopg2
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from shared_utils.db_utils import wait_for_db


def wait_for_db():
    """
    Ожидание готовности базы данных перед подключением
    
    Функция выполняет повторные попытки подключения к базе данных
    с интервалом ожидания между попытками. Это необходимо в Docker-среде,
    где база данных может запускаться с задержкой.
    
    Параметры:
        Нет
    
    Возвращает:
        None
    
    Исключения:
        psycopg2.OperationalError: если не удалось подключиться
        после максимального количества попыток
    
    Настройки:
        max_retries: максимальное количество попыток подключения (30)
        retry_delay: задержка между попытками в секундах (2)
    """
    max_retries = 30
    retry_delay = 2
    
    db_host = os.getenv('DB_HOST_LOCAL', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'calendar_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
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

# ============================================================================
# ОСНОВНОЙ БЛОК СКРИПТА
# ============================================================================

# Шаг 1: Ожидание готовности базы данных
print("Ожидание готовности базы данных...")
wait_for_db()

# Шаг 2: Установка соединения с базой данных
# Используем autocommit=True для автоматического применения изменений
db_host = os.getenv('DB_HOST_LOCAL', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'calendar_db')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'postgres')

conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    database=db_name,
    user=db_user,
    password=db_password
)
conn.autocommit = True
cur = conn.cursor()

print("Подключение к базе данных установлено.")

# ============================================================================
# СОЗДАНИЕ ТАБЛИЦ БАЗЫ ДАННЫХ
# ============================================================================

# ----------------------------------------------------------------------------
# Таблица 1: users
# Назначение: Хранение информации о пользователях Telegram-бота
# Связи: Является родительской таблицей для events, appointments, user_statistics
# ----------------------------------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id     BIGINT PRIMARY KEY,      -- Уникальный идентификатор пользователя в Telegram
    username        TEXT,                    -- Имя пользователя в Telegram (может быть пустым)
    first_name      TEXT,                    -- Имя пользователя
    last_name       TEXT,                    -- Фамилия пользователя
    email           TEXT,                    -- Email пользователя (опционально)
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата и время регистрации
    export_token    TEXT UNIQUE              -- Уникальный токен для экспорта данных
);
""")

# Обновление структуры таблицы users (добавление новых полей)
# Используем IF NOT EXISTS для безопасного добавления полей
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS export_token TEXT UNIQUE;")

# ----------------------------------------------------------------------------
# Таблица 2: events
# Назначение: Хранение событий, созданных пользователями
# Связи: Связана с users через внешний ключ (user_id)
#        Связана с appointments через внешний ключ (event_id)
# ----------------------------------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,         -- Автоинкрементный уникальный идентификатор
    user_id     BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,  -- Создатель события
    name        TEXT NOT NULL,              -- Название события
    event_date  DATE NOT NULL,              -- Дата события
    event_time  TIME NOT NULL,              -- Время события
    details     TEXT DEFAULT '',            -- Дополнительные детали события
    is_public   BOOLEAN DEFAULT FALSE       -- Флаг публичности события
);
""")

# ----------------------------------------------------------------------------
# Таблица 3: appointments
# Назначение: Хранение приглашений на события
# Связи: Связана с users через внешний ключ (organizer_id)
#        Связана с events через внешний ключ (event_id)
# ----------------------------------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id                      SERIAL PRIMARY KEY,         -- Автоинкрементный уникальный идентификатор
    organizer_id            BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,  -- Организатор
    event_id                INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,  -- Событие
    participant_telegram_id BIGINT NOT NULL,            -- Telegram ID приглашенного участника
    date                    DATE NOT NULL,              -- Дата приглашения
    time                    TIME NOT NULL,              -- Время приглашения
    details                 TEXT DEFAULT '',            -- Дополнительные детали
    status                  TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'declined', 'cancelled')),  -- Статус приглашения
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата создания приглашения
    UNIQUE (event_id, participant_telegram_id)  -- Уникальность: один участник не может быть приглашен дважды на одно событие
);
""")

# ----------------------------------------------------------------------------
# Таблица 4: bot_statistics
# Назначение: Хранение общей статистики использования бота по дням
# Связи: Нет внешних ключей (автономная таблица)
# ----------------------------------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS bot_statistics (
    date             DATE PRIMARY KEY,       -- Дата статистики
    user_count       INTEGER DEFAULT 0,      -- Количество пользователей
    event_count      INTEGER DEFAULT 0,      -- Количество созданных событий
    edited_events    INTEGER DEFAULT 0,      -- Количество отредактированных событий
    cancelled_events INTEGER DEFAULT 0       -- Количество отмененных событий
);
""")

# ----------------------------------------------------------------------------
# Таблица 5: user_statistics
# Назначение: Хранение индивидуальной статистики каждого пользователя
# Связи: Связана с users через внешний ключ (user_telegram_id)
# ----------------------------------------------------------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS user_statistics (
    user_telegram_id    BIGINT PRIMARY KEY REFERENCES users(telegram_id) ON DELETE CASCADE,  -- ID пользователя
    created_events      INTEGER DEFAULT 0,      -- Количество созданных событий пользователем
    edited_events       INTEGER DEFAULT 0,      -- Количество отредактированных событий
    cancelled_events    INTEGER DEFAULT 0,      -- Количество отмененных событий
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Дата последнего обновления статистики
);
""")

# ============================================================================
# ЗАВЕРШЕНИЕ РАБОТЫ
# ============================================================================

# Закрытие курсора и соединения с базой данных
cur.close()
conn.close()

# Вывод сообщений об успешном завершении
print("Все таблицы и поля созданы или обновлены.")
print("Теперь можно запускать бота и Django-админку без ошибок.")
print("Рекомендация: перезапустите Django-сервер и бота после выполнения.")