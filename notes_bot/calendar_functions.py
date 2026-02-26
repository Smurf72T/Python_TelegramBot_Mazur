# notes_bot/calendar_functions.py

import psycopg2
from psycopg2 import pool
from datetime import date, time
from db_config import DB_CONFIG


class Calendar:
    def __init__(self):
        self.pool = pool.ThreadedConnectionPool(
            minconn=DB_CONFIG["minconn"],
            maxconn=DB_CONFIG["maxconn"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )

    def _get_connection(self):
        return self.pool.getconn()

    def _put_connection(self, conn):
        self.pool.putconn(conn)

    # ─── Регистрация пользователя ─────────────────────────────
    def register_user(self, telegram_id: int, username: str = None) -> str:
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users (telegram_id, username)
                VALUES (%s, %s)
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
            self._put_connection(conn)

    # ─── Все остальные методы теперь требуют user_id ───────────
    def create_event(self, user_id: int, name: str, date_str: str, time_str: str, details: str = "") -> str:
        try:
            d = date.fromisoformat(date_str)
            t = time.fromisoformat(time_str)
        except ValueError:
            return "❌ Неверный формат! Дата: ГГГГ-ММ-ДД  Время: ЧЧ:ММ"

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO events (user_id, name, event_date, event_time, details)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (user_id, name.strip(), d, t, details.strip() or None)
            )
            event_id = cur.fetchone()[0]
            conn.commit()
            return f"✅ Событие «{name}» создано!\nID: {event_id}"
        except Exception as e:
            conn.rollback()
            return f"❌ Ошибка базы данных: {str(e)}"
        finally:
            cur.close()
            self._put_connection(conn)

    def list_events(self, user_id: int) -> str:
        conn = self._get_connection()
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
            self._put_connection(conn)

    def read_event(self, user_id: int, event_id: str) -> str:
        conn = self._get_connection()
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
            self._put_connection(conn)

    def edit_event(self, user_id: int, event_id: str, name=None, date=None, time=None, details=None) -> str:
        if all(v is None for v in (name, date, time, details)):
            return "Нечего изменять"

        conn = self._get_connection()
        try:
            cur = conn.cursor()
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name.strip())
            if date is not None:
                try:
                    d = date.fromisoformat(date)
                    updates.append("event_date = %s")
                    params.append(d)
                except ValueError:
                    return "❌ Неверный формат даты"
            if time is not None:
                try:
                    t = time.fromisoformat(time)
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
            self._put_connection(conn)

    def delete_event(self, user_id: int, event_id: str) -> str:
        conn = self._get_connection()
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
            self._put_connection(conn)

    def close(self):
        if hasattr(self, "pool") and self.pool:
            self.pool.closeall()