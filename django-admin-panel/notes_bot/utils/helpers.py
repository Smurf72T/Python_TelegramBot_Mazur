import os
import django
import uuid  # Для генерации уникальных идентификаторов

# Модуль secrets закомментирован из-за конфликта имён с файлом secrets.py в корне проекта
# Вместо secrets.token_urlsafe используем uuid4().hex для генерации токена

# Настройка Django перед импортом моделей
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from django.db import models
from telegram import Update
from telegram.ext import ContextTypes
from events.models.user_profile import UserProfile
from asgiref.sync import sync_to_async


def get_user_and_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает user_id и объект календаря из контекста.
    Устраняет дублирование кода в многочисленных обработчиках.
    
    Возвращает:
        tuple: (user_id, calendar_object)
    """
    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    return user_id, cal


def require_args(context, min_args=1, usage_message=None):
    """
    Проверяет наличие аргументов в команде.
    Устраняет дублирование проверок в обработчиках команд.
    
    Аргументы:
        context: контекст команды
        min_args: минимальное количество требуемых аргументов
        usage_message: сообщение об использовании (если None, используется стандартное)
    
    Возвращает:
        bool: True если аргументов достаточно, False в противном случае
    """
    if len(context.args) < min_args:
        return False
    return True


async def send_usage_message(update, command_name, example):
    """
    Отправляет сообщение об использовании команды.
    Устраняет дублирование сообщений об использовании.
    
    Аргументы:
        update: объект Update
        command_name: имя команды (для отображения)
        example: пример использования
    """
    await update.message.reply_text(f"Использование: {example}")


def clear_user_data(context):
    """
    Очищает user_data в контексте.
    Устраняет дублирование вызовов context.user_data.clear().
    
    Аргументы:
        context: контекст команды
    """
    context.user_data.clear()


def send_typing_action(func):
    """Декоратор для отправки действия "печатает" в Telegram."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action='typing'
        )
        return await func(update, context, *args, **kwargs)
    return wrapper


@sync_to_async
def get_user_by_telegram_id(telegram_id: int):
    """
    Получает пользователя по telegram_id.
    
    Аргументы:
        telegram_id (int): Telegram ID пользователя
    
    Возвращает:
        UserProfile: объект пользователя или None, если не найден
    """
    try:
        return UserProfile.objects.get(telegram_id=telegram_id)
    except UserProfile.DoesNotExist:
        return None


@sync_to_async
def create_user_if_not_exists(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """
    Создает пользователя, если он не существует, и генерирует для него уникальный токен экспорта.
    
    При создании нового пользователя автоматически генерируется и сохраняется токен в поле export_token,
    который может использоваться для безопасной выгрузки данных пользователя.
    
    Аргументы:
        telegram_id (int): Telegram ID пользователя
        username (str): Имя пользователя в Telegram
        first_name (str): Имя пользователя
        last_name (str): Фамилия пользователя
    
    Возвращает:
        UserProfile: объект пользователя (новый или существующий)
    """
    # Генерация уникального токена экспорта при создании нового пользователя
    # Используется uuid4().hex для генерации 32-символьной строки
    # Поле export_token в модели UserProfile имеет атрибут unique=True, что гарантирует уникальность
    token = uuid.uuid4().hex  # Генерирует строку длиной 32 символа
    
    user, created = UserProfile.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'export_token': token  # Сохраняем сгенерированный токен
        }
    )
    return user


@sync_to_async
def check_user_registered(telegram_id: int) -> bool:
    """
    Проверяет регистрацию пользователя.
    
    Аргументы:
        telegram_id (int): Telegram ID пользователя
    
    Возвращает:
        bool: True если пользователь зарегистрирован, False в противном случае
    """
    return UserProfile.objects.filter(telegram_id=telegram_id).exists()