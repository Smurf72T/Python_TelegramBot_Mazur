import os
import re

def sanitize_filename(name: str) -> str:
    """Очищает имя файла от запрещённых символов"""
    forbidden = r'[\\/*?:"<>|]'
    return re.sub(forbidden, "_", name.strip()[:100])  # максимум 100 символов


def note_path(note_name: str) -> str:
    os.makedirs("data/notes", exist_ok=True)
    return f"data/notes/{sanitize_filename(note_name)}.txt"


def create_note(note_name: str, note_text: str) -> str:
    name = sanitize_filename(note_name)
    path = note_path(name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(note_text)
    return f"✅ Заметка «{name}» успешно создана."


def read_note(note_name: str) -> str:
    path = note_path(note_name)
    if not os.path.isfile(path):
        return "❌ Заметка не найдена."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def edit_note(note_name: str, new_text: str) -> str:
    path = note_path(note_name)
    if not os.path.isfile(path):
        return "❌ Заметка не найдена."
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    return f"✅ Заметка «{note_name}» обновлена."


def delete_note(note_name: str) -> str:
    path = note_path(note_name)
    if not os.path.isfile(path):
        return "❌ Заметка не найдена."
    os.remove(path)
    return f"🗑 Заметка «{note_name}» удалена."


def list_notes(short_first: bool = True) -> str:
    notes = [f for f in os.listdir() if f.endswith(".txt")]
    if not notes:
        return "📭 Пока нет заметок."

    # Сортируем по длине имени файла
    notes_sorted = sorted(notes, key=len, reverse=not short_first)

    lines = []
    for fname in notes_sorted:
        name = fname[:-4]
        try:
            size = len(open(fname, encoding="utf-8").read())
            lines.append(f"• {name} ({size} символов)")
        except:
            lines.append(f"• {name}")

    order = "от короткой к длинной" if short_first else "от длинной к короткой"
    return f"📋 Все заметки ({order}):\n" + "\n".join(lines)