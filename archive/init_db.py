# init_db.py

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    database=DB_CONFIG["database"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"]
)
conn.autocommit = True
cur = conn.cursor()

# Создаём таблицу пользователей
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        TEXT,
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Пересоздаём таблицу событий с user_id (для чистоты проекта)
cur.execute("DROP TABLE IF EXISTS events;")
cur.execute("""
CREATE TABLE events (
    id          SERIAL          PRIMARY KEY,
    user_id     BIGINT          NOT NULL REFERENCES users(telegram_id),
    name        TEXT            NOT NULL,
    event_date  DATE            NOT NULL,
    event_time  TIME            NOT NULL,
    details     TEXT            DEFAULT ''
);
""")

cur.close()
conn.close()
print("✅ База данных обновлена: добавлены users + user_id в events")