"""
Модуль для управления пользователями в системе.

Предоставляет класс UserManager для регистрации пользователей
в Telegram-боте через Django ORM.
"""

from events.models import UserProfile


class UserManager:
    """
    Класс для управления пользователями в системе.
    """

    def register_user(self, telegram_id: int, username: str = None) -> str:
        """
        Регистрирует нового пользователя в системе.

        Если пользователь с таким Telegram ID уже существует, операция
        игнорируется (get_or_create).

        Args:
            telegram_id (int): Уникальный идентификатор пользователя в Telegram
            username (str, optional): Имя пользователя (может быть None)

        Returns:
            str: Сообщение об успешной регистрации или ошибке
        """
        try:
            UserProfile.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={"username": username},
            )
            return "✅ Вы успешно зарегистрированы в календаре!"
        except Exception as e:
            return f"❌ Ошибка регистрации: {str(e)}"
