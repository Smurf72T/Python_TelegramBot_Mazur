import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import os
import sys
import django

from db_config import DB_CONFIG
from .calendar_functions import Calendar

# Настраиваем Django-окружение (только один раз)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJANGO_PATH = os.path.join(BASE_DIR, 'django-admin-panel')
sys.path.insert(0, DJANGO_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from notes_bot.statistics import increment_stat

try:
    from secrets import TOKEN
except ImportError:
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Токен не найден")


# Состояния
NAME, DATE, TIME, DETAILS = range(4)
EDIT_FIELD, EDIT_VALUE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Календарь-бот (многопользовательский)\n\n"
        "Команды:\n"
        "/register       — зарегистрироваться\n"
        "/createevent    — добавить событие\n"
        "/listevents     — ваши события\n"
        "/readevent <id> — посмотреть событие\n"
        "/editevent <id> — изменить событие\n"
        "/deleteevent <id> — удалить событие\n"
        "/cancel         — отменить"
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    cal = context.bot_data["calendar"]
    result = cal.register_user(user_id, username)
    await update.message.reply_text(result)

    # Статистика: новый пользователь
    await increment_stat('user_count')


# ─── Создание события ───────────────────────────────────────
async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Название события?")
    return NAME


async def create_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Дата (ГГГГ-ММ-ДД)?")
    return DATE


async def create_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text.strip()
    await update.message.reply_text("Время (ЧЧ:ММ)?")
    return TIME


async def create_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time"] = update.message.text.strip()
    await update.message.reply_text("Описание (можно пустым):")
    return DETAILS


async def create_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name  = context.user_data.get("name", "").strip()
    date  = context.user_data.get("date", "").strip()
    time  = context.user_data.get("time", "").strip()
    descr = update.message.text.strip()

    if not name or not date or not time:
        await update.message.reply_text("Не заполнены обязательные поля.")
        context.user_data.clear()
        return ConversationHandler.END

    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    result = cal.create_event(user_id, name, date, time, descr)
    await update.message.reply_text(result)

    # Статистика: новое событие
    await increment_stat('event_count')

    context.user_data.clear()
    return ConversationHandler.END


# ─── Остальные команды с user_id ─────────────────────────────
async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    await update.message.reply_text(cal.list_events(user_id))


async def read_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напишите: /readevent 123")
        return
    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    await update.message.reply_text(cal.read_event(user_id, context.args[0]))


async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напишите: /deleteevent 123")
        return
    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    await update.message.reply_text(cal.delete_event(user_id, context.args[0]))


# ─── Редактирование события (по одному полю) ─────────────────
async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напишите: /editevent 123")
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


async def edit_choose_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.strip()
    if field not in ("1", "2", "3", "4"):
        await update.message.reply_text("Только цифры 1–4")
        return ConversationHandler.END

    context.user_data["edit_field"] = field
    await update.message.reply_text("Новое значение:")
    return EDIT_VALUE


async def edit_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eid   = context.user_data.get("edit_id")
    field = context.user_data.get("edit_field")
    value = update.message.text.strip()

    if not eid or not field:
        await update.message.reply_text("Ошибка данных. Начните заново /editevent")
        context.user_data.clear()
        return ConversationHandler.END

    mapping = {"1": "name", "2": "date", "3": "time", "4": "details"}
    user_id = update.effective_user.id
    cal = context.bot_data["calendar"]
    result = cal.edit_event(user_id, eid, **{mapping[field]: value})
    await update.message.reply_text(result)

    # Статистика: редактирование
    await increment_stat('edited_events')

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Действие отменено.")

    # Статистика: отмена
    await increment_stat('cancelled_events')


def main():
    calendar = Calendar()                           # создаём экземпляр здесь

    application = Application.builder() \
        .token(TOKEN) \
        .connection_pool_size(10) \
        .get_updates_connection_pool_size(10) \
        .read_timeout(30) \
        .write_timeout(30) \
        .connect_timeout(30) \
        .pool_timeout(30) \
        .build()

    # Сохраняем календарь в bot_data — будет доступен во всех обработчиках
    application.bot_data["calendar"] = calendar

    create_conv = ConversationHandler(
        entry_points=[CommandHandler("createevent", create_start)],
        states={
            NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, create_name)],
            DATE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, create_date)],
            TIME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, create_time)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_details)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation для редактирования
    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("editevent", edit_start)],
        states={
            EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_choose_field)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_set_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start",       start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(create_conv)
    application.add_handler(edit_conv)
    application.add_handler(CommandHandler("listevents",  list_events))
    application.add_handler(CommandHandler("readevent",   read_event))
    application.add_handler(CommandHandler("deleteevent", delete_event))
    application.add_handler(CommandHandler("cancel",      cancel))

    print("Многопользовательский Календарь-бот запущен...")

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        calendar.close()


if __name__ == "__main__":
    asyncio.run(main())