from typing import Dict, Any

from notes_bot.database import DatabasePool
from notes_bot.event_crud import EventCRUD

class AppointmentManager:
    """Класс для управления встречами и приглашениями пользователей.

    Атрибуты:
        db_pool (DatabasePool): Пул соединений с базой данных.
        event_crud (EventCRUD): Объект для операций с событиями.
    """

    def __init__(self, db_pool: DatabasePool, event_crud: EventCRUD):
        """Инициализирует менеджер встреч.

        Args:
            db_pool (DatabasePool): Пул соединений с базой данных.
            event_crud (EventCRUD): Объект для операций с событиями.
        """
        self.db_pool = db_pool
        self.event_crud = event_crud

    def create_appointment(self, organizer_id: int, event_id: int, participant_tg_id: int, details: str = "") -> str:
        """Создает приглашение на встречу для участника.

        Проверяет существование события, регистрацию участника и его доступность во времени.
        Создает приглашение со статусом 'pending'.

        Args:
            organizer_id (int): ID организатора встречи.
            event_id (int): ID события.
            participant_tg_id (int): Telegram ID участника.
            details (str, optional): Дополнительные детали приглашения. По умолчанию "".

        Returns:
            str: Сообщение о результате операции.

        Raises:
            ValueError: Если событие не существует, участник не зарегистрирован или недоступен.
        """
        # Проверка существования события
        event = self.event_crud.get_event_by_id(event_id)
        if not event:
            return f"Событие с ID {event_id} не найдено."

        # Проверка регистрации участника (упрощенная)
        # В реальной системе здесь будет проверка в базе данных
        if not self._is_user_registered(participant_tg_id):
            return f"Пользователь с Telegram ID {participant_tg_id} не зарегистрирован."

        # Проверка доступности участника во времени
        # Создание приглашения
        query = """
        INSERT INTO appointments (organizer_id, event_id, participant_tg_id, details, status)
        VALUES (?, ?, ?, ?, 'pending')
        """
        
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (organizer_id, event_id, participant_tg_id, details))
            conn.commit()
            
        return f"Приглашение на событие '{event['name']}' успешно отправлено пользователю {participant_tg_id}."

    def get_user_appointments(self, telegram_id: int, as_participant: bool = True) -> str:
        """Получает список встреч пользователя.

        Args:
            telegram_id (int): Telegram ID пользователя.
            as_participant (bool, optional): Получать как участника (True) или организатора (False). По умолчанию True.

        Returns:
            str: Форматированный список встреч в виде текстового сообщения.
        """
        if as_participant:
            query = """
            SELECT a.id, e.name, e.event_time, e.event_time, a.status, a.details
            FROM appointments a
            JOIN events e ON a.event_id = e.id
            WHERE a.participant_telegram_id = %s
            ORDER BY e.event_time
            """
        else:
            query = """
            SELECT a.id, e.name, e.event_time, e.event_time, a.status, a.details
            FROM appointments a
            JOIN events e ON a.event_id = e.id
            WHERE a.organizer_id = %s
            ORDER BY e.event_time
            """
        
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (telegram_id,))
            results = cursor.fetchall()
        
        if not results:
            role = "участника" if as_participant else "организатора"
            return f"Нет встреч для пользователя {telegram_id} в роли {role}."
        
        appointments = []
        for row in results:
            appointment = f"Встреча: {row[1]}\nВремя: {row[2]} - {row[3]}\nСтатус: {row[4]}\nДетали: {row[5] or 'Нет'}\n---"
            appointments.append(appointment)
        
        role = "участника" if as_participant else "организатора"
        return f"Встречи пользователя {telegram_id} в роли {role}:\n\n" + '\n'.join(appointments)

    def update_appointment_status(self, appointment_id: int, participant_id: int, new_status: str) -> str:
        """Обновляет статус приглашения.

        Args:
            appointment_id (int): ID приглашения.
            participant_id (int): ID участника (для проверки авторизации).
            new_status (str): Новый статус ('accepted', 'declined', 'pending').

        Returns:
            str: Сообщение о результате операции.

        Raises:
            ValueError: Если приглашение не найдено или участник не авторизован.
        """
        # Проверка допустимых статусов
        valid_statuses = ['accepted', 'declined', 'pending']
        if new_status not in valid_statuses:
            return f"Недопустимый статус: {new_status}. Допустимые значения: {', '.join(valid_statuses)}"
        
        # Проверка существования приглашения и прав участника
        query = """
        SELECT id FROM appointments 
        WHERE id = ? AND participant_tg_id = ?
        """
        
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (appointment_id, participant_id))
            appointment = cursor.fetchone()
            
        if not appointment:
            return f"Приглашение с ID {appointment_id} не найдено или вы не являетесь его участником."
        
        # Обновление статуса
        update_query = """
        UPDATE appointments 
        SET status = ?
        WHERE id = ?
        """
        
        with self.db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, (new_status, appointment_id))
            conn.commit()
        
        return f"Статус приглашения {appointment_id} успешно обновлен на '{new_status}'."
    
    def _is_user_registered(self, telegram_id: int) -> bool:
        """Проверяет, зарегистрирован ли пользователь в системе.

        Args:
            telegram_id (int): Telegram ID пользователя.

        Returns:
            bool: True, если пользователь зарегистрирован, иначе False.
        """
        # Заглушка для проверки регистрации пользователя
        # В реальной системе здесь будет запрос к базе данных
        return True
    
    def _is_user_available(self, telegram_id: int, start_time: str, end_time: str) -> bool:
        """Проверяет доступность пользователя во времени.

        Args:
            telegram_id (int): Telegram ID пользователя.
            start_time (str): Время начала события.
            end_time (str): Время окончания события.

        Returns:
            bool: True, если пользователь доступен, иначе False.
        """
        # Заглушка для проверки доступности пользователя
        # В реальной системе здесь будет проверка календаря пользователя
        return True
