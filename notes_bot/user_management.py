"""
Модуль для управления пользователями в системе.

Этот модуль предоставляет класс UserManager для регистрации и управления
пользователями в Telegram-боте через PostgreSQL базу данных.
"""

import psycopg2
from typing import Dict, Any

from notes_bot.database import DatabasePool


class UserManager:
    """
    Класс для управления пользователями в системе.

    Attributes:
        db_pool (DatabasePool): Экземпляр пула соединений с базой данных
    """

    def __init__(self, db_pool: DatabasePool) -> None:
        """
        Инициализирует UserManager с пулом соединений к базе данных.

        Args:
            db_pool (DatabasePool): Экземпляр DatabasePool для управления соединениями
        """
        self.db_pool = db_pool

    def register_user(self, telegram_id: int, username: str = None) -> str:
        """
        Регистрирует нового пользователя в системе.

        Метод добавляет пользователя в таблицу users с указанным telegram_id.
        Если пользователь с таким ID уже существует, операция игнорируется
        благодаря ON CONFLICT DO NOTHING.

        Использует контекстное управление соединением через db_pool.

        Args:
            telegram_id (int): Уникальный идентификатор пользователя в Telegram
            username (str, optional): Имя пользователя (может быть None)

        Returns:
            str: Сообщение об успешной регистрации или ошибке

        Example:
            >>> user_manager = UserManager(db_pool)
            >>> result = user_manager.register_user(123456789, "john_doe")
            >>> print(result)
            ✅ Вы успешно зарегистрированы в календаре!
        """
        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (telegram_id, username, registered_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (telegram_id) DO NOTHING
                """,
                (telegram_id, username)
            )
            conn.commit()
            return "✅ Вы успешно зарегистрированы в календаре!"
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка регистрации: {str(e)}"
        finally:
            cur.close()
            self.db_pool.put_connection(conn)