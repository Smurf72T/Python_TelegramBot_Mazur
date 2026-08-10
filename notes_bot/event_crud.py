from datetime import date, time

from events.models import Event

from notes_bot.statistics import increment_stat


class EventCRUD:
    """
    Класс для выполнения операций CRUD над событиями в Telegram-боте.

    Предоставляет методы для создания, чтения, обновления и удаления событий
    с использованием Django ORM. Все методы возвращают текстовые сообщения
    для отображения пользователю.
    """

    def create_event(self, user_id: int, name: str, date_str: str, time_str: str, details: str = "") -> str:
        """
        Создает новое событие для пользователя.

        Проверяет формат даты и времени, затем добавляет событие в базу данных.

        Returns:
            str: Сообщение об успешном создании или ошибке
        """
        try:
            d = date.fromisoformat(date_str)
            t = time.fromisoformat(time_str)
        except ValueError:
            return "❌ Неверный формат! Дата: ГГГГ-ММ-ДД  Время: ЧЧ:ММ"

        try:
            event = Event.objects.create(
                user_id=user_id,
                name=name.strip(),
                event_date=d,
                event_time=t,
                details=details.strip() or "",
                is_public=False,
            )
        except Exception as e:
            return f"❌ Ошибка базы данных: {str(e)}"

        increment_stat("event_count", user_id)
        return f"✅ Событие «{event.name}» создано!\nID: {event.id}"

    def list_events(self, user_id: int) -> str:
        """
        Возвращает список всех событий пользователя.

        Returns:
            str: Отформатированный список событий или сообщение об их отсутствии
        """
        events = Event.objects.filter(user_id=user_id).order_by("event_date", "event_time")
        if not events:
            return "📭 У вас пока нет событий."

        lines = ["📋 Ваши события:"]
        for event in events:
            lines.append(f"• #{event.id} | {event.event_date} {event.event_time} | {event.name}")
        return "\n".join(lines)

    def read_event(self, user_id: int, event_id: str) -> str:
        """
        Получает подробную информацию о конкретном событии.

        Returns:
            str: Детальная информация о событии или сообщение об ошибке
        """
        event = Event.objects.filter(id=event_id, user_id=user_id).first()
        if not event:
            return "❌ Событие не найдено или не принадлежит вам."

        return (f"📅 Событие #{event.id}\n"
                f"Название: {event.name}\n"
                f"Дата:   {event.event_date}\n"
                f"Время:   {event.event_time}\n"
                f"Описание: {event.details or '—'}")

    def edit_event(self, user_id: int, event_id: str, name=None, new_date=None, new_time=None, details=None) -> str:
        """
        Редактирует существующее событие.

        Позволяет изменять любые поля события по отдельности.
        Проверяет формат даты и времени при их изменении.

        Returns:
            str: Сообщение об успешном редактировании или ошибке
        """
        if all(v is None for v in (name, new_date, new_time, details)):
            return "Нечего изменять"

        updates = {}

        if name is not None:
            updates["name"] = name.strip()
        if new_date is not None:
            try:
                updates["event_date"] = date.fromisoformat(new_date)
            except ValueError:
                return "❌ Неверный формат даты"
        if new_time is not None:
            try:
                updates["event_time"] = time.fromisoformat(new_time)
            except ValueError:
                return "❌ Неверный формат времени"
        if details is not None:
            updates["details"] = details.strip() or ""

        updated = Event.objects.filter(id=event_id, user_id=user_id).update(**updates)
        if updated == 0:
            return "❌ Событие не найдено или не принадлежит вам"

        increment_stat("edited_events", user_id)
        return f"✅ Событие #{event_id} обновлено"

    def delete_event(self, user_id: int, event_id: str) -> str:
        """
        Удаляет событие пользователя.

        Returns:
            str: Сообщение об успешном удалении или ошибке
        """
        deleted, _ = Event.objects.filter(id=event_id, user_id=user_id).delete()
        if deleted == 0:
            return "❌ Событие не найдено или не принадлежит вам"

        increment_stat("cancelled_events", user_id)
        return f"🗑 Событие #{event_id} удалено"

    def get_event_by_id(self, event_id) -> Event:
        """
        Возвращает объект события по ID.

        Args:
            event_id: ID события

        Returns:
            Event: объект события или None, если событие не найдено
        """
        return Event.objects.filter(id=event_id).first()
