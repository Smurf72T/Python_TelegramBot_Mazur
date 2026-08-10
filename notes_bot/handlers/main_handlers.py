from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import uuid

from asgiref.sync import sync_to_async

from notes_bot.utils.helpers import (
    get_user_by_telegram_id,
    create_user_if_not_exists,
    send_typing_action,
    check_user_registered
)


@send_typing_action
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
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
    """Обработчик команды /register для регистрации/обновления профиля пользователя"""
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
        await update.message.reply_text("Профиль успешно создан!")
        return

    # Синхронизируем данные профиля с данными Telegram
    updated = False
    fields = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    for field, value in fields.items():
        if value and getattr(context_user, field) != value:
            setattr(context_user, field, value)
            updated = True

    # Гарантируем наличие токена экспорта для безопасной выгрузки
    if not context_user.export_token:
        context_user.export_token = uuid.uuid4().hex
        updated = True

    if updated:
        await sync_to_async(context_user.save)()
        await update.message.reply_text("Профиль успешно обновлён!")
    else:
        await update.message.reply_text("Твой профиль уже заполнен и актуален!")


@send_typing_action
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /cancel для отмены текущего действия"""
    await update.message.reply_text(
        'Действие отменено. Если нужно что-то сделать - просто скажи!'
    )
    return ConversationHandler.END


@send_typing_action
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /help
    Отправляет сообщение с описанием всех доступных команд бота
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