import psycopg2.pool
from typing import Dict, Any

class DatabasePool:
    """Менеджер пула соединений с PostgreSQL для многопоточных приложений.

    Attributes:
        config (Dict[str, Any]): Конфигурация подключения к базе данных
        pool (psycopg2.pool.ThreadedConnectionPool): Пул соединений
    """

    def __init__(self, config: Dict[str, Any]):
        """Инициализирует пул соединений с базой данных.

        Args:
            config (Dict[str, Any]): Словарь с параметрами подключения:
                - host: хост базы данных
                - port: порт базы данных
                - database: имя базы данных
                - user: имя пользователя
                - password: пароль пользователя
                - minconn: минимальное количество соединений в пуле
                - maxconn: максимальное количество соединений в пуле
        """
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
