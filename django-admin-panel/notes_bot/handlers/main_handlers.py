"""
Модуль main_handlers.py — основные обработчики команд бота

Содержит обработчики основных команд: /start, /register, /cancel, /help.
Эти обработчики обеспечивают первичное взаимодействие с пользователем,
регистрацию и предоставление справочной информации.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from asgiref.sync import sync_to_async

from notes_bot.utils.helpers import (
    get_user_by_telegram_id,
    create_user_if_not_exists,
    send_typing_action,
    check_user_registered
)


@send_typing_action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start — первая точка входа в бота.

    Проверяет наличие пользователя в базе данных. Если пользователь новый —
    автоматически создаёт его профиль и предлагает заполнить дополнительную информацию.
    Если пользователь уже существует — приветствует его.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        None: Отправляет приветственное сообщение

    Command usage:
        /start

    Process:
        1. Получает данные пользователя из update
        2. Проверяет наличие в базе данных
        3. Если нет — создаёт новый профиль
        4. Отправляет приветственное сообщение с инструкциями
    """
    user = update.effective_user
    context_user = await get_user_by_telegram_id(user.id)

    if not context_user:
        await create_user_if_not_exists(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        await update.message.reply_text(
            f"Привет, {user.first_name}! Ты успешно зарегистрирован."
            " Используй /register, чтобы заполнить профиль."
        )
    else:
        await update.message.reply_text(
            f"С возвращением, {user.first_name}!"
            " Используй /register, чтобы обновить профиль."
        )


@send_typing_action
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /register — заполнение профиля пользователя.

    Получает или создаёт профиль пользователя, заполняет недостающие данные
    (имя, фамилию) из данных Telegram и сохраняет изменения.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        None: Отправляет сообщение об успешной регистрации или что профиль уже заполнен

    Command usage:
        /register

    Process:
        1. Получает или создаёт профиль пользователя
        2. Проверяет заполненность имени и фамилии
        3. Заполняет недостающие поля из данных Telegram
        4. Сохраняет изменения в базе данных
    """
    user = update.effective_user

    # Получаем или создаем пользователя
    context_user = await get_user_by_telegram_id(user.id)
    if not context_user:
        context_user = await create_user_if_not_exists(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

    # Проверяем, заполнен ли профиль
    if context_user.first_name and context_user.last_name:
        await update.message.reply_text(
            "Твой профиль уже заполнен!"
        )
    else:
        # Заполняем недостающие данные
        updated_fields = {}
        if not context_user.first_name:
            updated_fields['first_name'] = user.first_name
        if not context_user.last_name:
            updated_fields['last_name'] = user.last_name

        for field, value in updated_fields.items():
            setattr(context_user, field, value)
        
        await sync_to_async(context_user.save)()
        
        await update.message.reply_text(
            "Профиль успешно обновлён!"
        )


@send_typing_action
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработчик команды /cancel — отмена текущего диалога/действия.

    Используется в ConversationHandler для выхода из текущего диалога
    и очистки временных данных пользователя.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        int: ConversationHandler.END для завершения диалога

    Command usage:
        /cancel

    Process:
        1. Отправляет сообщение об отмене действия
        2. Возвращает ConversationHandler.END для завершения диалога
    """
    await update.message.reply_text(
        'Действие отменено. Если нужно что-то сделать - просто скажи!'
    )
    return ConversationHandler.END


@send_typing_action
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help — отображение справки по командам бота.

    Формирует и отправляет пользователю полное описание всех доступных команд
    с кратким описанием назначения каждой команды.

    Args:
        update: Объект обновления от Telegram
        context: Контекст команды

    Returns:
        None: Отправляет сообщение со списком всех команд

    Command usage:
        /help

    Process:
        1. Формирует текст справки со всеми командами
        2. Отправляет сообщение пользователю
    """
    help_text = (
        "/start - Начать работу с ботом\n"
        "/register - Зарегистрироваться в системе\n"
        "/createevent - Создать новое событие\n"
        "/listevents - Просмотреть свои события\n"
        "/readevent - Прочитать детали события\n"
        "/editevent - Изменить событие\n"
        "/deleteevent - Удалить событие\n"
        "/appoint - Назначить встречу\n"
        "/myappointments - Мои назначенные встречи\n"
        "/myinvites - Мои приглашения\n"
        "/confirm - Подтвердить встречу\n"
        "/decline - Отклонить встречу\n"
        "/mycalendar - Показать календарь\n"
        "/publicevent - Сделать событие публичным/приватным\n"
        "/publicevents - Просмотр публичных событий\n"
        "/export - Экспортировать события\n"
        "/help - Показать это меню"
    )
    await update.message.reply_text(help_text)