"""
Модуль event_validator.py — валидаторы для работы с событиями

Содержит функции для валидации названия, описания, ID события и других полей.
"""

def validate_event_name(name: str) -> tuple:
    """
    Валидирует название события.
    
    Аргументы:
        name (str): Название события
    
    Возвращает:
        tuple: (успех: bool, сообщение об ошибке или None)
    """
    if not name or len(name.strip()) == 0:
        return False, "Название события не может быть пустым"
    if len(name) > 255:
        return False, "Название события слишком длинное (макс. 255 символов)"
    return True, None


def validate_event_details(details: str) -> tuple:
    """
    Валидирует описание события.
    
    Аргументы:
        details (str): Описание события
    
    Возвращает:
        tuple: (успех: bool, сообщение об ошибке или None)
    """
    if not details:
        return True, None
    if len(details) > 1000:
        return False, "Описание слишком длинное (макс. 1000 символов)"
    return True, None


def validate_event_id(event_id: str) -> tuple:
    """
    Валидирует ID события.
    
    Аргументы:
        event_id (str): ID события в виде строки
    
    Возвращает:
        tuple: (успех: bool, event_id как int при успехе или сообщение об ошибке)
    """
    if not event_id or len(event_id.strip()) == 0:
        return False, "ID события не может быть пустым"
    if not event_id.isdigit():
        return False, "ID события должен быть числом"
    return True, int(event_id)
