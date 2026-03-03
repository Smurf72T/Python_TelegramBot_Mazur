"""
Модуль db_utils.py — утилиты для работы с базой данных

Содержит общие функции для работы с PostgreSQL базой данных, которые используются
в разных частях приложения (бот, инициализация, администрирование).
"""

import time
import psycopg2
from psycopg2 import OperationalError
from db_config import DB_CONFIG


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
        except OperationalError as e:
            if attempt == max_retries - 1:
                print(f"Не удалось подключиться к базе данных после {max_retries} попыток: {e}")
                raise
            print(f"Попытка {attempt + 1}/{max_retries}: База данных не готова, ждем {retry_delay} сек...")
            time.sleep(retry_delay)