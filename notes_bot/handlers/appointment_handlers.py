"""
Модуль appointment_handlers.py — обработчики команд управления встречами

Содержит обработчики команд для назначения встреч, просмотра приглашений и подтверждения участия.
Выносит логику обработки команд из основного модуля бота для улучшения читаемости и поддержки.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


# Импортируем валидаторы

from notes_bot.validators.user_validator import validate_telegram_id
from notes_bot.validators.event_validator import validate_event_id

# Импортируем общие вспомогательные функции
from notes_bot.utils.helpers import get_user_and_calendar


# Состояния для диалогов
APPOINT_COMMENT = 0


# Функция вынесена в notes_bot.utils.helpers


async def appoint_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /appoint <event_id> <telegram_id>")
        return ConversationHandler.END
    
    # Валидация event_id
    is_valid, event_id = validate_event_id(context.args[0])
    if not is_valid:
        await update.message.reply_text(event_id)
        return ConversationHandler.END
    
    # Валидация telegram_id
    is_valid, telegram_id = validate_telegram_id(context.args[1])
    if not is_valid:
        await update.message.reply_text(telegram_id)
        return ConversationHandler.END
    
    context.user_data["appoint_event_id"] = event_id
    context.user_data["appoint_participant"] = telegram_id
    await update.message.reply_text("Комментарий к приглашению (или /skip):")
    return APPOINT_COMMENT


async def _create_appointment_from_context(update: Update, context: ContextTypes.DEFAULT_TYPE, details: str = ""):
    cal = context.bot_data["calendar"]
    organizer_id = update.effective_user.id
    event_id = context.user_data["appoint_event_id"]
    participant = int(context.user_data["appoint_participant"])

    result = cal.create_appointment(organizer_id, event_id, participant, details)
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


async def appoint_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    details = "" if text == "/skip" else text.strip()
    return await _create_appointment_from_context(update, context, details)


async def appoint_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропускает комментарий при создании приглашения (без деталей)."""
    return await _create_appointment_from_context(update, context, "")


async def my_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает встречи, на которые пользователь приглашен как участник.
    Использует вспомогательную функцию get_user_and_calendar для устранения дублирования.
    """
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_user_appointments(user_id, as_participant=True))



async def my_invites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает встречи, которые пользователь организовал как приглашающий.
    Использует вспомогательную функцию get_user_and_calendar для устранения дублирования.
    """
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_user_appointments(user_id, as_participant=False))



async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подтверждает приглашение на встречу.
    Проверяет наличие аргументов с помощью require_args.
    """
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /confirm <appointment_id>")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.update_appointment_status(int(context.args[0]), user_id, "confirmed")
    await update.message.reply_text(result)


async def decline_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отклоняет приглашение на встречу.
    Проверяет наличие аргументов с помощью require_args.
    """
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /decline <appointment_id>")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.update_appointment_status(int(context.args[0]), user_id, "declined")
    await update.message.reply_text(result)