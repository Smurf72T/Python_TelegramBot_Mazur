from typing import Optional

from events.models import Event


class PublicEventsManager:
    """
    Менеджер управления публичными событиями для бота заметок.

    Предоставляет функционал для управления видимостью событий и получения
    списка публичных событий от других пользователей через Django ORM.
    """

    def toggle_public(self, user_id: int, event_id: str) -> str:
        """
        Переключает видимость события (публичное/приватное).

        Args:
            user_id (int): ID пользователя (владельца события).
            event_id (str): ID события.

        Returns:
            str: Сообщение о результате операции.
        """
        try:
            event = Event.objects.get(id=event_id, user_id=user_id)
        except Event.DoesNotExist:
            return f"Событие {event_id} не найдено или доступ запрещён"

        event.is_public = not event.is_public
        event.save(update_fields=["is_public"])

        status_text = "публичным" if event.is_public else "приватным"
        return f"Событие успешно сделано {status_text}"

    def get_public_events(self, current_user_id: Optional[int] = None) -> str:
        """
        Возвращает список всех публичных событий от других пользователей.

        Args:
            current_user_id (Optional[int]): ID текущего пользователя. Если передан,
                его события будут исключены из результата.

        Returns:
            str: Отформатированный список публичных событий.
        """
        events = Event.objects.filter(is_public=True).select_related("user")
        if current_user_id is not None:
            events = events.exclude(user_id=current_user_id)
        events = events.order_by("event_date", "event_time")

        if not events:
            return "Нет доступных публичных событий"

        message_parts = ["Доступные публичные события:\n"]
        for event in events:
            author_name = event.user.username if event.user and event.user.username else "Аноним"
            event_info = f"• {author_name}: {event.name} ({event.event_date} {event.event_time})"
            if event.details:
                event_info += f" - {event.details}"
            message_parts.append(event_info)

        return "\n".join(message_parts)
