from typing import Optional

from notes_bot.user_management import UserManager
from notes_bot.event_crud import EventCRUD
from notes_bot.appointment_manager import AppointmentManager
from notes_bot.public_events import PublicEventsManager


class Calendar:
    """
    Фасадный класс для управления календарем событий и встреч в Telegram-боте.

    Этот класс предоставляет единый интерфейс для всех операций с календарем,
    делегируя реальную работу соответствующим менеджерам. Он обеспечивает полную
    обратную совместимость с оригинальным классом Calendar из calendar_functions.py.

    Атрибуты:
        user_manager (UserManager): Менеджер пользователей
        event_crud (EventCRUD): Менеджер операций с событиями
        appointment_manager (AppointmentManager): Менеджер встреч и приглашений
        public_events_manager (PublicEventsManager): Менеджер публичных событий
    """

    def __init__(self):
        """
        Инициализирует фасадный класс Calendar, создавая все необходимые менеджеры.

        Доступ к базе данных осуществляется через Django ORM.
        """
        self.user_manager = UserManager()
        self.event_crud = EventCRUD()
        self.appointment_manager = AppointmentManager(self.event_crud)
        self.public_events_manager = PublicEventsManager()

    def register_user(self, telegram_id: int, username: str = None) -> str:
        """
        Регистрирует нового пользователя в системе.

        Returns:
            str: Сообщение об успешной регистрации или ошибке
        """
        return self.user_manager.register_user(telegram_id, username)

    def create_event(self, user_id: int, name: str, date_str: str, time_str: str, details: str = "") -> str:
        """
        Создает новое событие для пользователя.

        Returns:
            str: Сообщение об успешном создании или ошибке
        """
        return self.event_crud.create_event(user_id, name, date_str, time_str, details)

    def list_events(self, user_id: int) -> str:
        """
        Возвращает список всех событий пользователя.

        Returns:
            str: Отформатированный список событий или сообщение об их отсутствии
        """
        return self.event_crud.list_events(user_id)

    def read_event(self, user_id: int, event_id: str) -> str:
        """
        Получает подробную информацию о конкретном событии.

        Returns:
            str: Детальная информация о событии или сообщение об ошибке
        """
        return self.event_crud.read_event(user_id, event_id)

    def edit_event(self, user_id: int, event_id: str, name=None, new_date=None, new_time=None, details=None) -> str:
        """
        Редактирует существующее событие.

        Returns:
            str: Сообщение об успешном редактировании или ошибке
        """
        return self.event_crud.edit_event(user_id, event_id, name, new_date, new_time, details)

    def delete_event(self, user_id: int, event_id: str) -> str:
        """
        Удаляет событие пользователя.

        Returns:
            str: Сообщение об успешном удалении или ошибке
        """
        return self.event_crud.delete_event(user_id, event_id)

    def create_appointment(self, organizer_id: int, event_id: int, participant_tg_id: int, details: str = "") -> str:
        """
        Создает приглашение на встречу для участника.

        Returns:
            str: Сообщение об успешном создании приглашения или ошибке
        """
        return self.appointment_manager.create_appointment(organizer_id, event_id, participant_tg_id, details)

    def get_user_appointments(self, telegram_id: int, as_participant: bool = True) -> str:
        """
        Получает список встреч пользователя.

        Args:
            telegram_id (int): Telegram ID пользователя
            as_participant (bool): Если True - встречи, куда пригласили пользователя;
                                   если False - встречи, которые он создал

        Returns:
            str: Отформатированный список встреч или сообщение об их отсутствии
        """
        return self.appointment_manager.get_user_appointments(telegram_id, as_participant)

    def update_appointment_status(self, appointment_id: int, participant_id: int, new_status: str) -> str:
        """
        Обновляет статус встречи для участника.

        Returns:
            str: Сообщение об успешном изменении статуса или ошибке
        """
        return self.appointment_manager.update_appointment_status(appointment_id, participant_id, new_status)

    def toggle_public(self, user_id: int, event_id: str) -> str:
        """
        Переключает флаг публичности события.

        Returns:
            str: Сообщение об успешном изменении статуса или ошибке
        """
        return self.public_events_manager.toggle_public(user_id, event_id)

    def get_public_events(self, current_user_id: Optional[int] = None) -> str:
        """
        Возвращает все публичные события других пользователей.

        Returns:
            str: Отформатированный список публичных событий или сообщение об их отсутствии
        """
        return self.public_events_manager.get_public_events(current_user_id)

    def close(self) -> None:
        """
        Заглушка для обратной совместимости.

        Соединениями с базой данных управляет Django ORM, поэтому
        явное закрытие пула больше не требуется.
        """
        pass
