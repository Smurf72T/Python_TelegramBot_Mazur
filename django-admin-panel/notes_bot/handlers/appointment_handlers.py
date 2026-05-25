"""
Модуль appointment_handlers.py — обработчики команд управления встречами

Содержит обработчики команд для назначения встреч, просмотра приглашений и подтверждения участия.
Выносит логику обработки команд из основного модуля бота для улучшения читаемости и поддержки.

Основные функции:
- appoint_start: начало процесса создания приглашения
- appoint_details: завершение создания приглашения с комментарием
- my_appointments: просмотр назначенных пользователю встреч
- my_invites: просмотр встреч, созданных пользователем
- confirm_appointment: подтверждение участия во встрече
- decline_appointment: отклонение приглашения на встречу
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from notes_bot.calendar_functions import Calendar

# Импортируем валидаторы
from notes_bot.validators.user_validator import validate_telegram_id
from notes_bot.validators.event_validator import validate_event_id

# Импортируем общие вспомогательные функции
from notes_bot.utils.helpers import get_user_and_calendar


# Состояния для диалогов
APPOINT_COMMENT = 0


# Функция вынесена в notes_bot.utils.helpers


async def appoint_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начинает процесс создания приглашения на встречу.

    Проверяет наличие аргументов (event_id и telegram_id), валидирует их
    и переводит диалог в состояние ожидания комментария.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами

    Returns:
        int: Состояние APPOINT_COMMENT или ConversationHandler.END при ошибке

    Command usage:
        /appoint <event_id> <telegram_id>

    Example:
        /appoint 123 987654321
    """
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
    
    # Сохраняем данные для следующего шага диалога
    context.user_data["appoint_event_id"] = event_id
    context.user_data["appoint_participant"] = telegram_id
    await update.message.reply_text("Комментарий к приглашению (или /skip):")
    return APPOINT_COMMENT


async def appoint_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Завершает процесс создания приглашения на встречу.

    Получает комментарий пользователя (или пропускает его), создаёт приглашение
    через менеджер календаря и очищает временные данные.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с сохранёнными данными

    Returns:
        int: ConversationHandler.END после завершения

    Process:
        1. Получает текст сообщения или пропускает (если /skip)
        2. Создаёт приглашение через Calendar.create_appointment()
        3. Очищает временные данные пользователя
    """
    text = update.message.text
    details = "" if text == "/skip" else text.strip()

    cal = context.bot_data["calendar"]
    organizer_id = update.effective_user.id
    event_id = context.user_data["appoint_event_id"]
    participant = int(context.user_data["appoint_participant"])

    result = cal.create_appointment(organizer_id, event_id, participant, details)
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


async def my_appointments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает встречи, на которые пользователь приглашен как участник.

    Получает Telegram ID пользователя из update и использует менеджер календаря
    для получения списка приглашений, где пользователь выступает участником.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Command usage:
        /myappointments

    Returns:
        None: Отправляет сообщение со списком встреч или сообщением об их отсутствии
    """
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_user_appointments(user_id, as_participant=True))


async def my_invites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает встречи, которые пользователь организовал как приглашающий.

    Получает Telegram ID пользователя из update и использует менеджер календаря
    для получения списка встреч, которые пользователь создал и куда пригласил других.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Command usage:
        /myinvites

    Returns:
        None: Отправляет сообщение со списком встреч или сообщением об их отсутствии
    """
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.get_user_appointments(user_id, as_participant=False))


async def confirm_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подтверждает участие пользователя во встрече.

    Проверяет наличие appointment_id в аргументах команды и обновляет статус
    приглашения на 'confirmed' для указанного пользователя.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами

    Command usage:
        /confirm <appointment_id>

    Example:
        /confirm 456

    Returns:
        None: Отправляет сообщение об успешном подтверждении или ошибке
    """
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /confirm <appointment_id>")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.update_appointment_status(int(context.args[0]), user_id, "confirmed")
    await update.message.reply_text(result)


async def decline_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отклоняет приглашение пользователя на встречу.

    Проверяет наличие appointment_id в аргументах команды и обновляет статус
    приглашения на 'declined' для указанного пользователя.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами

    Command usage:
        /decline <appointment_id>

    Example:
        /decline 456

    Returns:
        None: Отправляет сообщение об успешном отклонении или ошибке
    """
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /decline <appointment_id>")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.update_appointment_status(int(context.args[0]), user_id, "declined")
    await update.message.reply_text(result)