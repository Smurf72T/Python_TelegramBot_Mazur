"""
Модуль user_validator.py — валидаторы для работы с пользователями

Содержит функции для валидации данных пользователя: Telegram ID, имя пользователя и другие параметры.
"""


def validate_telegram_id(user_id: str) -> tuple:
    """
    Валидирует Telegram ID пользователя.
    
    Аргументы:
        user_id (str): Telegram ID пользователя
    
    Возвращает:
        tuple: (успех: bool, объект int или сообщение об ошибке)
    """
    try:
        user_id_int = int(user_id.strip())
        if user_id_int <= 0:
            return False, "Telegram ID должен быть положительным числом"
        return True, user_id_int
    except ValueError:
        return False, "Telegram ID должен быть числом"


def validate_username(username: str) -> tuple:
    """
    Валидирует имя пользователя.
    
    Аргументы:
        username (str): Имя пользователя
    
    Возвращает:
        tuple: (успех: bool, сообщение об ошибке или None)
    """
    if username is None:
        return True, None
    if len(username) > 50:
        return False, "Имя пользователя слишком длинное (макс. 50 символов)"
    if not username.isalnum() and '_' not in username:
        return False, "Имя пользователя может содержать только буквы, цифры и символ _"
    return True, None