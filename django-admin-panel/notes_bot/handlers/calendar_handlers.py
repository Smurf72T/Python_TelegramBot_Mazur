"""
Модуль calendar_handlers.py — обработчики команд управления календарем

Содержит обработчики команд для просмотра личного кабинета, публичных событий и управления публичностью.
Выносит логику обработки команд из основного модуля бота для улучшения читаемости и поддержки.
"""

from telegram import Update
from telegram.ext import ContextTypes

from notes_bot.calendar_functions import Calendar

# Импортируем общие вспомогательные функции
from notes_bot.utils.helpers import get_user_and_calendar, require_args, send_usage_message, clear_user_data


# Функции вынесены в notes_bot.utils.helpers


async def my_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает личный кабинет пользователя со статистикой, событиями и публичными событиями.

    Формирует комплексное представление о деятельности пользователя:
    - Личная статистика (в разработке)
    - Список личных событий
    - Список публичных событий других пользователей

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Command usage:
        /mycalendar

    Returns:
        None: Отправляет сообщение с полным личным кабинетом
    """
    user_id, cal = get_user_and_calendar(update, context)

    events_text = cal.list_events(user_id)
    stats_text = "Статистика: в разработке"
    public_text = cal.get_public_events()

    await update.message.reply_text(
        f"👤 **Личный кабинет**\n"
        f"Telegram ID: `{user_id}`\n\n"
        f"{stats_text}\n\n"
        f"{events_text}\n\n"
        f"{public_text}\n\n"
        f"Для выгрузки календаря используйте /export",
        parse_mode="Markdown"
    )


async def toggle_public_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Переключает статус публичности события (публичное/приватное).

    Меняет флаг is_public у указанного события пользователя.
    Если событие было публичным - становится приватным и наоборот.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами (event_id)

    Command usage:
        /publicevent <event_id>

    Example:
        /publicevent 123

    Returns:
        None: Отправляет сообщение об успешном изменении или ошибке
    """
    if not require_args(context, 1):
        await send_usage_message(update, "publicevent", "/publicevent <id>")
        return

    event_id = context.args[0]
    user_id, cal = get_user_and_calendar(update, context)

    result = cal.toggle_public(user_id, event_id)
    await update.message.reply_text(result)


async def public_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает все публичные события других пользователей.

    Получает список всех событий, у которых флаг is_public установлен в True.
    Позволяет пользователям видеть события, которые другие сделали общедоступными.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Command usage:
        /publicevents

    Returns:
        None: Отправляет сообщение со списком публичных событий или сообщением об их отсутствии
    """
    _, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_public_events())
