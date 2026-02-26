import os
import json
from datetime import datetime

class Calendar:
    def __init__(self):
        self.file_path = "data/events.json"
        os.makedirs("data", exist_ok=True)
        self.events = self._load_events()

    def _load_events(self) -> dict:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_events(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def create_event(self, name: str, date: str, time: str, details: str = "") -> str:
        """Возвращает сообщение для пользователя"""
        try:
            # Проверка формата даты
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return "❌ Неверный формат даты или времени!\nИспользуй: ГГГГ-ММ-ДД и ЧЧ:ММ"

        event_id = str(len(self.events) + 1)
        self.events[event_id] = {
            "id": event_id,
            "name": name.strip(),
            "date": date,
            "time": time,
            "details": details.strip()
        }
        self._save_events()
        return f"✅ Событие «{name}» создано!\nID: {event_id}"

    def read_event(self, event_id: str) -> str:
        if event_id not in self.events:
            return "❌ Событие не найдено."
        e = self.events[event_id]
        return (f"📅 Событие #{e['id']}\n"
                f"Название: {e['name']}\n"
                f"Дата: {e['date']}\n"
                f"Время: {e['time']}\n"
                f"Описание: {e['details'] or '—'}")

    def edit_event(self, event_id: str, name: str = None, date: str = None,
                   time: str = None, details: str = None) -> str:
        if event_id not in self.events:
            return "❌ Событие не найдено."

        if name: self.events[event_id]["name"] = name.strip()
        if date: self.events[event_id]["date"] = date
        if time: self.events[event_id]["time"] = time
        if details is not None: self.events[event_id]["details"] = details.strip()

        self._save_events()
        return f"✅ Событие #{event_id} обновлено."

    def delete_event(self, event_id: str) -> str:
        if event_id not in self.events:
            return "❌ Событие не найдено."
        del self.events[event_id]
        self._save_events()
        return f"🗑 Событие #{event_id} удалено."

    def list_events(self) -> str:
        if not self.events:
            return "📭 Пока нет событий в календаре."

        lines = ["📋 Список всех событий:"]
        for eid, e in sorted(self.events.items(), key=lambda x: x[1]["date"]):
            lines.append(f"• #{eid} | {e['date']} {e['time']} | {e['name']}")
        return "\n".join(lines)


# Глобальный экземпляр (будет импортирован в bot.py)
calendar = Calendar()