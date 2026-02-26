# init_db.py

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**{
    k: v for k, v in DB_CONFIG.items() if k in ("host", "port", "database", "user", "password")
})

conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL          PRIMARY KEY,
    name        TEXT            NOT NULL,
    event_date  DATE            NOT NULL,
    event_time  TIME            NOT NULL,
    details     TEXT            DEFAULT ''
);
""")

cur.close()
conn.close()

print("Таблица events создана или уже существует.")