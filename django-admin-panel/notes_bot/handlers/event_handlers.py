"""
Модуль event_handlers.py — обработчики команд управления событиями

Содержит обработчики команд для создания, просмотра, редактирования и удаления событий.
Выносит логику обработки команд из основного модуля бота для улучшения читаемости и поддержки.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from notes_bot.calendar_functions import Calendar

# Импортируем валидаторы
from notes_bot.validators.event_validator import validate_event_name, validate_event_details
from notes_bot.validators.date_validator import validate_date
from notes_bot.validators.time_validator import validate_time

# Импортируем общие вспомогательные функции
from notes_bot.utils.helpers import get_user_and_calendar, require_args, send_usage_message, clear_user_data


# Состояния для диалогов
NAME, DATE, TIME, DETAILS = range(4)
EDIT_FIELD, EDIT_VALUE = range(2)


# Функции вынесены в notes_bot.utils.helpers


async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начинает процесс создания нового события.

    Запрашивает у пользователя название события и переводит диалог
    в состояние ожидания ввода названия.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        int: Состояние NAME для ожидания ввода названия

    Command usage:
        /createevent
    """
    await update.message.reply_text("Название события?")
    return NAME


async def create_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает ввод названия события.

    Сохраняет название в user_data и запрашивает дату события.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        int: Состояние DATE для ожидания ввода даты
    """
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Дата (ГГГГ-ММ-ДД)?")
    return DATE


async def create_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает ввод даты события.

    Сохраняет дату в user_data и запрашивает время события.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        int: Состояние TIME для ожидания ввода времени
    """
    context.user_data["date"] = update.message.text.strip()
    await update.message.reply_text("Время (ЧЧ:ММ)?")
    return TIME


async def create_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает ввод времени события.

    Сохраняет время в user_data и запрашивает описание события.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        int: Состояние DETAILS для ожидания ввода описания
    """
    context.user_data["time"] = update.message.text.strip()
    await update.message.reply_text("Описание (можно пустым):")
    return DETAILS


async def create_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершает создание события, сохраняя все данные.
    Проверяет заполнение обязательных полей и использует вспомогательные функции.
    """
    name = context.user_data.get("name", "").strip()
    date_str = context.user_data.get("date", "").strip()
    time_str = context.user_data.get("time", "").strip()
    descr = update.message.text.strip()

    # Валидация названия события
    is_valid, error = validate_event_name(name)
    if not is_valid:
        await update.message.reply_text(error)
        clear_user_data(context)
        return ConversationHandler.END

    # Валидация даты
    is_valid, date_obj = validate_date(date_str)
    if not is_valid:
        await update.message.reply_text(error)
        clear_user_data(context)
        return ConversationHandler.END

    # Валидация времени
    is_valid, time_obj = validate_time(time_str)
    if not is_valid:
        await update.message.reply_text(error)
        clear_user_data(context)
        return ConversationHandler.END

    # Валидация описания события
    is_valid, error = validate_event_details(descr)
    if not is_valid:
        await update.message.reply_text(error)
        clear_user_data(context)
        return ConversationHandler.END

    user_id, cal = get_user_and_calendar(update, context)
    result = cal.create_event(user_id, name, date_str, time_str, descr)
    await update.message.reply_text(result)

    clear_user_data(context)
    return ConversationHandler.END


async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает список всех событий пользователя.

    Получает Telegram ID пользователя и использует менеджер календаря
    для получения отформатированного списка всех событий.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Command usage:
        /listevents

    Returns:
        None: Отправляет сообщение со списком событий или сообщением об их отсутствии
    """
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.list_events(user_id))


async def read_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает детальную информацию о конкретном событии.

    Проверяет наличие event_id в аргументах команды и получает подробную
    информацию о событии через менеджер календаря.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами (event_id)

    Command usage:
        /readevent <event_id>

    Example:
        /readevent 123

    Returns:
        None: Отправляет сообщение с деталями события или ошибкой
    """
    if not require_args(context, 1):
        await send_usage_message(update, "readevent", "/readevent 123")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    await update.message.reply_text(cal.read_event(user_id, context.args[0]))


async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Удаляет событие по идентификатору.

    Проверяет наличие event_id в аргументах команды, удаляет событие
    через менеджер календаря и отправляет результат пользователю.
    Поддерживает работу как с текстовыми командами, так и с callback-кнопками.

    Args:
        update: Объект обновления от Telegram (может быть message или callback_query)
        context: Контекст команды с аргументами (event_id)

    Command usage:
        /deleteevent <event_id>

    Example:
        /deleteevent 123

    Returns:
        None: Отправляет сообщение об успешном удалении или ошибке
    """
    if not require_args(context, 1):
        await send_usage_message(update, "deleteevent", "/deleteevent 123")
        return
    
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.delete_event(user_id, context.args[0])
    
    # Проверяем, вызван ли обработчик через callback-кнопку
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(result)
    elif update.message:
        await update.message.reply_text(result)



async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Начинает процесс редактирования события.

    Проверяет наличие event_id в аргументах команды, сохраняет его в user_data
    и отображает меню выбора поля для редактирования.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с аргументами (event_id)

    Returns:
        int: Состояние EDIT_FIELD для ожидания выбора поля или ConversationHandler.END при ошибке

    Command usage:
        /editevent <event_id>

    Example:
        /editevent 123

    Process:
        1. Проверяет наличие event_id
        2. Сохраняет ID в user_data
        3. Отображает меню выбора поля (1-4)
    """
    if not require_args(context, 1):
        await send_usage_message(update, "editevent", "/editevent 123")
        return ConversationHandler.END

    eid = context.args[0].strip()
    context.user_data["edit_id"] = eid

    await update.message.reply_text(
        "Что меняем?\n"
        "1 = название\n"
        "2 = дата\n"
        "3 = время\n"
        "4 = описание\n"
        "Введите цифру:"
    )
    return EDIT_FIELD


async def edit_choose_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обрабатывает выбор поля для редактирования.

    Проверяет корректность введенной цифры (1-4), сохраняет выбор в user_data
    и запрашивает новое значение у пользователя.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды с сохранённым event_id

    Returns:
        int: Состояние EDIT_VALUE для ожидания нового значения или ConversationHandler.END при ошибке

    Process:
        1. Проверяет, что введена цифра от 1 до 4
        2. Сохраняет выбор поля в user_data
        3. Запрашивает новое значение
    """
    field = update.message.text.strip()
    if field not in ("1", "2", "3", "4"):
        await update.message.reply_text("Только цифры 1–4")
        return ConversationHandler.END

    context.user_data["edit_field"] = field
    await update.message.reply_text("Новое значение:")
    return EDIT_VALUE


async def edit_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Устанавливает новое значение для выбранного поля события.
    Использует вспомогательные функции для устранения дублирования.
    """
    eid = context.user_data.get("edit_id")
    field = context.user_data.get("edit_field")
    value = update.message.text.strip()

    if not eid or not field:
        await update.message.reply_text("Ошибка данных. Начните заново /editevent")
        clear_user_data(context)
        return ConversationHandler.END

    mapping = {"1": "name", "2": "new_date", "3": "new_time", "4": "details"}
    user_id, cal = get_user_and_calendar(update, context)
    result = cal.edit_event(user_id, eid, **{mapping[field]: value})
    await update.message.reply_text(result)

    clear_user_data(context)
    return ConversationHandler.END