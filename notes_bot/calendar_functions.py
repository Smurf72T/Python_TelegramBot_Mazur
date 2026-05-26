
# Этот файл является точкой входа для обратной совместимости.
# Основная реализация перемещена в calendar_interface.py и другие модули.

from .calendar_interface import Calendar

__all__ = ["Calendar"]
