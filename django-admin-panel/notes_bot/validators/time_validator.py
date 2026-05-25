"""
Модуль time_validator.py — валидаторы для работы со временем

Содержит функции для валидации и конвертации строк со временем в объекты datetime.time.
"""

from datetime import time, datetime


def validate_time(time_str: str) -> tuple:
    """
    Валидирует строку со временем и возвращает объект time.
    
    Аргументы:
        time_str (str): Строка со временем в формате ЧЧ:ММ
    
    Возвращает:
        tuple: (успех: bool, объект time или сообщение об ошибке)
    """
    try:
        return True, datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        return False, "Неверный формат времени! Используйте ЧЧ:ММ"