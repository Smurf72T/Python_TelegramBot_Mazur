"""
Модуль db_utils.py — утилиты для работы с базой данных

Содержит общие функции для работы с PostgreSQL базой данных, которые используются
в разных частях приложения (бот, инициализация, администрирование).
"""

import os
import time
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()


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
    
    # Определяем окружение
    run_env = os.getenv("RUN_ENV", "local")
    
    # Получаем настройки БД из переменных окружения
    if run_env == "docker":
        db_host = os.getenv("DB_HOST_DOCKER", "db")
    else:
        db_host = os.getenv("DB_HOST_LOCAL", "localhost")
    
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "calendar_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    
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
        except OperationalError as e:
            if attempt == max_retries - 1:
                print(f"Не удалось подключиться к базе данных после {max_retries} попыток: {e}")
                raise
            print(f"Попытка {attempt + 1}/{max_retries}: База данных не готова, ждем {retry_delay} сек...")
            time.sleep(retry_delay)