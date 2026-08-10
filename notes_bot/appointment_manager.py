from django.db import IntegrityError

from events.models import Appointment, UserProfile

from notes_bot.event_crud import EventCRUD


class AppointmentManager:
    """Класс для управления встречами и приглашениями пользователей.

    Атрибуты:
        event_crud (EventCRUD): Объект для операций с событиями.
    """

    VALID_STATUSES = ('pending', 'confirmed', 'declined', 'cancelled')

    def __init__(self, event_crud: EventCRUD):
        """Инициализирует менеджер встреч.

        Args:
            event_crud (EventCRUD): Объект для операций с событиями.
        """
        self.event_crud = event_crud

    def create_appointment(self, organizer_id: int, event_id: int, participant_tg_id: int, details: str = "") -> str:
        """Создает приглашение на встречу для участника.

        Проверяет существование события и регистрацию участника,
        затем создает приглашение со статусом 'pending'.

        Returns:
            str: Сообщение о результате операции.
        """
        event = self.event_crud.get_event_by_id(event_id)
        if not event:
            return f"Событие с ID {event_id} не найдено."

        if not self._is_user_registered(participant_tg_id):
            return f"Пользователь с Telegram ID {participant_tg_id} не зарегистрирован."

        try:
            Appointment.objects.create(
                organizer_telegram_id=organizer_id,
                event=event,
                participant_telegram_id=participant_tg_id,
                date=event.event_date,
                time=event.event_time,
                details=details,
                status="pending",
            )
        except IntegrityError:
            return f"Пользователь {participant_tg_id} уже приглашён на это событие."
        except Exception as e:
            return f"❌ Ошибка базы данных: {str(e)}"

        return f"Приглашение на событие «{event.name}» успешно отправлено пользователю {participant_tg_id}."

    def get_user_appointments(self, telegram_id: int, as_participant: bool = True) -> str:
        """Получает список встреч пользователя.

        Args:
            telegram_id (int): Telegram ID пользователя.
            as_participant (bool): Если True - встречи, куда пригласили пользователя;
                                   если False - встречи, которые он организовал.

        Returns:
            str: Форматированный список встреч в виде текстового сообщения.
        """
        if as_participant:
            query = Appointment.objects.filter(participant_telegram_id=telegram_id)
            role = "участника"
        else:
            query = Appointment.objects.filter(organizer_telegram_id=telegram_id)
            role = "организатора"

        appointments = query.select_related("event").order_by("event__event_date", "event__event_time")

        if not appointments:
            return f"Нет встреч для пользователя {telegram_id} в роли {role}."

        parts = [f"Встречи пользователя {telegram_id} в роли {role}:", ""]
        for appointment in appointments:
            parts.append(f"Встреча: {appointment.event.name}")
            parts.append(f"Время: {appointment.time}")
            parts.append(f"Статус: {appointment.status}")
            parts.append(f"Детали: {appointment.details or 'Нет'}")
            parts.append("---")
        return "\n".join(parts)

    def update_appointment_status(self, appointment_id: int, participant_id: int, new_status: str) -> str:
        """Обновляет статус приглашения.

        Args:
            appointment_id (int): ID приглашения.
            participant_id (int): Telegram ID участника (для проверки прав).
            new_status (str): Новый статус ('pending', 'confirmed', 'declined', 'cancelled').

        Returns:
            str: Сообщение о результате операции.
        """
        if new_status not in self.VALID_STATUSES:
            return f"Недопустимый статус: {new_status}. Допустимые значения: {', '.join(self.VALID_STATUSES)}"

        updated = Appointment.objects.filter(
            id=appointment_id,
            participant_telegram_id=participant_id,
        ).update(status=new_status)

        if updated == 0:
            return f"Приглашение с ID {appointment_id} не найдено или вы не являетесь его участником."

        return f"Статус приглашения {appointment_id} успешно обновлен на '{new_status}'."

    def _is_user_registered(self, telegram_id: int) -> bool:
        """Проверяет, зарегистрирован ли пользователь в системе.

        Returns:
            bool: True, если пользователь зарегистрирован, иначе False.
        """
        return UserProfile.objects.filter(telegram_id=telegram_id).exists()
