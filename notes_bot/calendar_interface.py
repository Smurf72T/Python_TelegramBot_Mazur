import os
import sys

# Добавляем корневую директорию в путь для импорта db_config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from notes_bot.database import DatabasePool
from notes_bot.user_management import UserManager
from notes_bot.event_crud import EventCRUD
from notes_bot.appointment_manager import AppointmentManager
from notes_bot.public_events import PublicEventsManager
from shared_utils.db_config import DB_CONFIG


class Calendar:
    """
    Фасадный класс для управления календарем событий и встреч в Telegram-боте.

    Этот класс предоставляет единый интерфейс для всех операций с календарем,
    делегируя реальную работу соответствующим менеджерам. Он обеспечивает полную
    обратную совместимость с оригинальным классом Calendar из calendar_functions.py.

    Атрибуты:
        db_pool (DatabasePool): Пул соединений с базой данных
        user_manager (UserManager): Менеджер пользователей
        event_crud (EventCRUD): Менеджер операций с событиями
        appointment_manager (AppointmentManager): Менеджер встреч и приглашений
        public_events_manager (PublicEventsManager): Менеджер публичных событий
    """

    def __init__(self):
        """
        Инициализирует фасадный класс Calendar, создавая все необходимые менеджеры.

        Создает экземпляры всех менеджеров и настраивает их взаимодействие.
        Использует конфигурацию из глобальной переменной DB_CONFIG для подключения к базе данных.
        """
        # Создаем пул соединений
        self.db_pool = DatabasePool(DB_CONFIG)
        
        # Инициализируем все менеджеры с необходимыми зависимостями
        self.user_manager = UserManager(self.db_pool)
        self.event_crud = EventCRUD(self.db_pool)
        self.appointment_manager = AppointmentManager(self.db_pool, self.event_crud)
        self.public_events_manager = PublicEventsManager(self.db_pool, self.event_crud)

    def register_user(self, telegram_id: int, username: str = None) -> str:
        """
        Регистрирует нового пользователя в системе.

        Делегирует вызов менеджеру пользователей.

        Args:
            telegram_id (int): Уникальный идентификатор пользователя в Telegram
            username (str, optional): Имя пользователя (может быть None)

        Returns:
            str: Сообщение об успешной регистрации или ошибке
        """
        return self.user_manager.register_user(telegram_id, username)

    def create_event(self, user_id: int, name: str, date_str: str, time_str: str, details: str = "") -> str:
        """
        Создает новое событие для пользователя.

        Делегирует вызов менеджеру событий.

        Args:
            user_id (int): ID пользователя, создающего событие
            name (str): Название события
            date_str (str): Дата в формате ГГГГ-ММ-ДД
            time_str (str): Время в формате ЧЧ:ММ
            details (str, optional): Дополнительные детали события

        Returns:
            str: Сообщение об успешном создании или ошибке
        """
        return self.event_crud.create_event(user_id, name, date_str, time_str, details)

    def list_events(self, user_id: int) -> str:
        """
        Возвращает список всех событий пользователя.

        Делегирует вызов менеджеру событий.

        Args:
            user_id (int): ID пользователя, чьи события нужно получить

        Returns:
            str: Отформатированный список событий или сообщение об их отсутствии
        """
        return self.event_crud.list_events(user_id)

    def read_event(self, user_id: int, event_id: str) -> str:
        """
        Получает подробную информацию о конкретном событии.

        Делегирует вызов менеджеру событий.

        Args:
            user_id (int): ID пользователя
            event_id (str): ID события

        Returns:
            str: Детальная информация о событии или сообщение об ошибке
        """
        return self.event_crud.read_event(user_id, event_id)

    def edit_event(self, user_id: int, event_id: str, name=None, date=None, time=None, details=None) -> str:
        """
        Редактирует существующее событие.

        Делегирует вызов менеджеру событий.

        Args:
            user_id (int): ID пользователя
            event_id (str): ID события для редактирования
            name (optional): Новое название
            date (optional): Новая дата
            time (optional): Новое время
            details (optional): Новые детали

        Returns:
            str: Сообщение об успешном редактировании или ошибке
        """
        return self.event_crud.edit_event(user_id, event_id, name, date, time, details)

    def delete_event(self, user_id: int, event_id: str) -> str:
        """
        Удаляет событие пользователя.

        Делегирует вызов менеджеру событий.

        Args:
            user_id (int): ID пользователя
            event_id (str): ID события для удаления

        Returns:
            str: Сообщение об успешном удалении или ошибке
        """
        return self.event_crud.delete_event(user_id, event_id)

    def create_appointment(self, organizer_id: int, event_id: int, participant_tg_id: int, details: str = "") -> str:
        """
        Создает приглашение на встречу для участника.

        Делегирует вызов менеджеру встреч.

        Args:
            organizer_id (int): ID организатора встречи
            event_id (int): ID события, к которому создается приглашение
            participant_tg_id (int): Telegram ID участника
            details (str, optional): Дополнительные детали встречи

        Returns:
            str: Сообщение об успешном создании приглашения или ошибке
        """
        return self.appointment_manager.create_appointment(organizer_id, event_id, participant_tg_id, details)

    def get_user_appointments(self, telegram_id: int, as_participant: bool = True) -> str:
        """
        Получает список встреч пользователя.

        Делегирует вызов менеджеру встреч.

        Args:
            telegram_id (int): Telegram ID пользователя
            as_participant (bool): Если True - возвращает встречи, куда пригласили пользователя.
                                 Если False - возвращает встречи, которые он создал

        Returns:
            str: Отформатированный список встреч или сообщение об их отсутствии
        """
        return self.appointment_manager.get_user_appointments(telegram_id, as_participant)

    def update_appointment_status(self, appointment_id: int, participant_id: int, new_status: str) -> str:
        """
        Обновляет статус встречи для участника.

        Делегирует вызов менеджеру встреч.

        Args:
            appointment_id (int): ID встречи
            participant_id (int): Telegram ID участника
            new_status (str): Новый статус ('pending', 'confirmed', 'declined')

        Returns:
            str: Сообщение об успешном изменении статуса или ошибке
        """
        return self.appointment_manager.update_appointment_status(appointment_id, participant_id, new_status)

    def toggle_public(self, user_id: int, event_id: str) -> str:
        """
        Переключает флаг публичности события.

        Делегирует вызов менеджеру публичных событий.

        Args:
            user_id (int): ID пользователя
            event_id (str): ID события

        Returns:
            str: Сообщение об успешном изменении статуса или ошибке
        """
        return self.public_events_manager.toggle_public(user_id, event_id)

    def get_public_events(self) -> str:
        """
        Возвращает все публичные события других пользователей.

        Делегирует вызов менеджеру публичных событий.

        Returns:
            str: Отформатированный список публичных событий или сообщение об их отсутствии
        """
        return self.public_events_manager.get_public_events()

    def close(self) -> None:
        """
        Закрывает все соединения в пуле.

        Метод для корректного завершения работы с базой данных.
        Должен вызываться при завершении работы приложения.
        """
        if hasattr(self, "db_pool") and self.db_pool:
            self.db_pool.closeall()
