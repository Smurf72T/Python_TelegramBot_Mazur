"""
Модуль date_validator.py — валидаторы для работы с датой

Содержит функции для валидации и конвертации строк с датой в объекты datetime.date.
"""

from datetime import date, datetime


def validate_date(date_str: str) -> tuple:
    """
    Валидирует строку с датой и возвращает объект date.
    
    Аргументы:
        date_str (str): Строка с датой в формате ГГГГ-ММ-ДД
    
    Возвращает:
        tuple: (успех: bool, объект date или сообщение об ошибке)
    """
    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        if parsed_date < date.today():
            return False, "Дата не может быть в прошлом"
        return True, parsed_date
    except ValueError:
        return False, "Неверный формат даты! Используйте ГГГГ-ММ-ДД"