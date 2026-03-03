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
    Использует вспомогательную функцию get_user_and_calendar для устранения дублирования.
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
    Проверяет наличие аргументов с помощью require_args.
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
    Показывает все публичные события.
    Использует вспомогательную функцию get_user_and_calendar для устранения дублирования.
    """
    _, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_public_events())