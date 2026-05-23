import os
import psycopg2.pool
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class DatabasePool:
    """Менеджер пула соединений с PostgreSQL для многопоточных приложений.

    Attributes:
        config (Dict[str, Any]): Конфигурация подключения к базе данных
        pool (psycopg2.pool.ThreadedConnectionPool): Пул соединений
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Инициализирует пул соединений с базой данных.

        Args:
            config (Optional[Dict[str, Any]]): Словарь с параметрами подключения.
                Если не передан, параметры берутся из переменных окружения:
                - DB_HOST_LOCAL: хост базы данных
                - DB_PORT: порт
                - DB_NAME: имя базы данных
                - DB_USER: имя пользователя
                - DB_PASSWORD: пароль
                - DB_MINCONN: мин. количество соединений
                - DB_MAXCONN: макс. количество соединений
        """
        if config is None:
            config = {
                'host': os.getenv('DB_HOST_LOCAL', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'calendar_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'postgres'),
                'minconn': int(os.getenv('DB_MINCONN', 1)),
                'maxconn': int(os.getenv('DB_MAXCONN', 20)),
            }
        
        self.config = config
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=config.get('minconn', 1),
            maxconn=config.get('maxconn', 20),
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )

    def get_connection(self):
        """Возвращает соединение из пула.

        Returns:
            psycopg2.extensions.connection: Соединение с базой данных

        Raises:
            psycopg2.pool.PoolError: Если нет доступных соединений в пуле
        """
        return self.pool.getconn()

    def put_connection(self, conn) -> None:
        """Возвращает соединение обратно в пул.

        Args:
            conn (psycopg2.extensions.connection): Соединение для возврата в пул
        """
        self.pool.putconn(conn)

    def closeall(self) -> None:
        """Закрывает все соединения в пуле."""
        if self.pool:
            self.pool.closeall()
