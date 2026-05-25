"""
Модуль export_handlers.py — обработчики команд экспорта данных

Содержит обработчики команд для экспорта календаря в различные форматы.
Выносит логику обработки команд из основного модуля бота для улучшения читаемости и поддержки.
"""

from datetime import datetime
import httpx

from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from notes_bot.calendar_functions import Calendar

# Импортируем общие вспомогательные функции
from notes_bot.utils.helpers import get_user_and_calendar


# Функция вынесена в notes_bot.utils.helpers


async def export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    from events.models import UserProfile
    profile = await sync_to_async(UserProfile.objects.get)(telegram_id=user_id)

    keyboard = [
        [
            InlineKeyboardButton("CSV", callback_data=f"export_csv_{user_id}_{profile.export_token}"),
            InlineKeyboardButton("JSON", callback_data=f"export_json_{user_id}_{profile.export_token}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выберите формат выгрузки календаря:",
        reply_markup=reply_markup
    )


async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split('_')
    fmt = parts[1]  # csv или json
    user_id = int(parts[2])
    token = parts[3]

    if fmt == "csv":
        url = f"http://django:8000/export/events/?user_id={user_id}&token={token}"
        ext = "csv"
    else:
        url = f"http://django:8000/export/events/json/?user_id={user_id}&token={token}"
        ext = "json"

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"calendar_{user_id}_{today}.{ext}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()  # Проверка на ошибки HTTP (4xx, 5xx)
            content = response.content
            content_type = response.headers.get('content-type', 'application/octet-stream')
    except httpx.RequestError as e:
        await query.message.reply_text(
            f"❌ Ошибка при подключении к серверу экспорта: {e}\n\n"
            f"Попробуйте позже или обратитесь к администратору."
        )
        return
    except httpx.HTTPStatusError as e:
        await query.message.reply_text(
            f"❌ Сервер экспорта вернул ошибку {e.response.status_code}.\n"
            f"Возможно, токен недействителен или данные отсутствуют."
        )
        return

    # Проверяем, что контент не пустой
    if not content:
        await query.message.reply_text(
            "❌ Получен пустой файл от сервера экспорта. "
            "Попробуйте позже или обратитесь к администратору."
        )
        return

    # Отправляем файл пользователю
    try:
        await query.message.reply_document(
            document=content,
            filename=filename,
            caption=f"📁 Ваш календарь в формате {ext.upper()}"
        )
    except TelegramError as e:
        await query.message.reply_text(
            f"❌ Не удалось отправить файл: {e}\n\n"
            f"Попробуйте позже или обратитесь к администратору."
        )
        return