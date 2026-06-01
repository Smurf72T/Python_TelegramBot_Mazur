from datetime import date, time


from notes_bot.database import DatabasePool

class EventCRUD:
    """
    Класс для выполнения операций CRUD над событиями в Telegram-боте.
    
    Предоставляет методы для создания, чтения, обновления и удаления событий
    с использованием пула соединений к базе данных. Все методы возвращают
    текстовые сообщения для отображения пользователю.
    """

    def __init__(self, db_pool: DatabasePool):
        """
        Инициализирует экземпляр EventCRUD с пулом соединений к базе данных.
        
        Args:
            db_pool (DatabasePool): Пул соединений для работы с базой данных
        """
        self.db_pool = db_pool

    def create_event(self, user_id: int, name: str, date_str: str, time_str: str, details: str = "") -> str:
        """
        Создает новое событие для пользователя.
        
        Метод проверяет формат даты и времени, затем добавляет событие
        в базу данных. Все события по умолчанию создаются как публичные.
        
        Args:
            user_id (int): ID пользователя, создающего событие
            name (str): Название события
            date_str (str): Дата в формате ГГГГ-ММ-ДД
            time_str (str): Время в формате ЧЧ:ММ
            details (str, optional): Дополнительные детали события
        
        Returns:
            str: Сообщение об успешном создании или ошибке
        """
        try:
            d = date.fromisoformat(date_str)
            t = time.fromisoformat(time_str)
        except ValueError:
            return "❌ Неверный формат! Дата: ГГГГ-ММ-ДД  Время: ЧЧ:ММ"

        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO events (user_id, name, event_date, event_time, details, is_public)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, name.strip(), d, t, details.strip() or None, False)
            )
            event_id = cur.fetchone()[0]
            conn.commit()
            return f"✅ Событие «{name}» создано!\nID: {event_id}"
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка базы данных: {str(e)}"
        finally:
            cur.close()
            self.db_pool.put_connection(conn)

    def list_events(self, user_id: int) -> str:
        """
        Возвращает список всех событий пользователя.
        
        Получает все события, принадлежащие указанному пользователю,
        и форматирует их для отображения в виде списка.
        
        Args:
            user_id (int): ID пользователя, чьи события нужно получить
        
        Returns:
            str: Отформатированный список событий или сообщение об их отсутствии
        """
        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, event_date, event_time
                FROM events
                WHERE user_id = %s
                ORDER BY event_date, event_time
                """,
                (user_id,)
            )
            rows = cur.fetchall()
            if not rows:
                return "📭 У вас пока нет событий."
            lines = ["📋 Ваши события:"]
            for eid, name, dt, tm in rows:
                lines.append(f"• #{eid} | {dt} {tm} | {name}")
            return "\n".join(lines)
        finally:
            cur.close()
            self.db_pool.put_connection(conn)

    def read_event(self, user_id: int, event_id: str) -> str:
        """
        Получает подробную информацию о конкретном событии.
        
        Args:
            user_id (int): ID пользователя
            event_id (str): ID события
        
        Returns:
            str: Детальная информация о событии или сообщение об ошибке
        """
        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, event_date, event_time, details
                FROM events
                WHERE id = %s AND user_id = %s
                """,
                (event_id, user_id)
            )
            row = cur.fetchone()
            if not row:
                return "❌ Событие не найдено или не принадлежит вам."
            eid, name, dt, tm, details = row
            return (f"📅 Событие #{eid}\n"
                    f"Название: {name}\n"
                    f"Дата:   {dt}\n"
                    f"Время:   {tm}\n"
                    f"Описание: {details or '—'}")
        finally:
            cur.close()
            self.db_pool.put_connection(conn)

    def edit_event(self, user_id: int, event_id: str, name=None, new_date=None, new_time=None, details=None) -> str:
        """
        Редактирует существующее событие.
        
        Позволяет изменять любые поля события по отдельности.
        Проверяет формат даты и времени при их изменении.
        
        Args:
            user_id (int): ID пользователя
            event_id (str): ID события для редактирования
            name (optional): Новое название
            new_date (optional): Новая дата
            new_time (optional): Новое время
            details (optional): Новые детали
        
        Returns:
            str: Сообщение об успешном редактировании или ошибке
        """
        if all(v is None for v in (name, new_date, new_time, details)):
            return "Нечего изменять"

        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name.strip())
            if new_date is not None:
                try:
                    d = date.fromisoformat(new_date)
                    updates.append("event_date = %s")
                    params.append(d)
                except ValueError:
                    return "❌ Неверный формат даты"
            if new_time is not None:
                try:
                    t = time.fromisoformat(new_time)
                    updates.append("event_time = %s")
                    params.append(t)
                except ValueError:
                    return "❌ Неверный формат времени"
            if details is not None:
                updates.append("details = %s")
                params.append(details.strip() or None)

            params.extend([event_id, user_id])
            query = f"UPDATE events SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
            cur.execute(query, params)
            if cur.rowcount == 0:
                conn.rollback()
                return "❌ Событие не найдено или не принадлежит вам"
            conn.commit()
            return f"✅ Событие #{event_id} обновлено"
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка: {str(e)}"
        finally:
            cur.close()
            self.db_pool.put_connection(conn)

    def delete_event(self, user_id: int, event_id: str) -> str:
        """
        Удаляет событие пользователя.
        
        Args:
            user_id (int): ID пользователя
            event_id (str): ID события для удаления
        
        Returns:
            str: Сообщение об успешном удалении или ошибке
        """
        conn = self.db_pool.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM events WHERE id = %s AND user_id = %s",
                (event_id, user_id)
            )
            if cur.rowcount == 0:
                conn.rollback()
                return "❌ Событие не найдено или не принадлежит вам"
            conn.commit()
            return f"🗑 Событие #{event_id} удалено"
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка: {str(e)}"
        finally:
            cur.close()
            self.db_pool.put_connection(conn)
