import asyncio
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from .calendar_functions import calendar

from .notes_functions import (
    create_note, read_note, edit_note, delete_note, list_notes
)

try:
    from secrets import TOKEN
except ImportError:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Токен не найден! Создай secrets.py или установи переменную окружения.")

# Состояния для ConversationHandler
NAME, TEXT = range(2)
EDIT_NAME, EDIT_TEXT = range(2)

# Состояния для календаря
EVENT_NAME, EVENT_DATE, EVENT_TIME, EVENT_DETAILS = range(4)
EDIT_EVENT_ID, EDIT_EVENT_FIELD = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для заметок.\n\n"
        "Доступные команды:\n"
        "/create — создать заметку\n"
        "/read <название> — прочитать\n"
        "/edit <название> — редактировать\n"
        "/delete <название> — удалить\n"
        "/list — список (короткие первыми)\n"
        "/listlong — список (длинные первыми)\n"
        "/cancel — отменить текущее действие\n"
        "/createevent — создать событие\n"
        "/readevent <ID> — прочитать событие\n"
        "/editevent <ID> — редактировать событие\n"
        "/deleteevent <ID> — удалить событие\n"
        "/listevents — список всех событий\n"
    )


# ====================== СОЗДАНИЕ ЗАМЕТКИ ======================
async def create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как назвать заметку?")
    return NAME


async def create_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["note_name"] = update.message.text.strip()
    await update.message.reply_text("Теперь введи текст заметки:")
    return TEXT


async def create_get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("note_name")
    text = update.message.text
    result = create_note(name, text)
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.")
    context.user_data.clear()
    return ConversationHandler.END


# ====================== ЧТЕНИЕ ======================
async def read_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /read Название заметки")
        return
    name = " ".join(context.args)
    result = read_note(name)
    await update.message.reply_text(result)


# ====================== УДАЛЕНИЕ ======================
async def delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /delete Название заметки")
        return
    name = " ".join(context.args)
    result = delete_note(name)
    await update.message.reply_text(result)


# ====================== СПИСОК ======================
async def list_short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(list_notes(short_first=True))


async def list_long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(list_notes(short_first=False))


# ====================== РЕДАКТИРОВАНИЕ (по аналогии с create) ======================
async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /edit Название заметки")
        return ConversationHandler.END
    context.user_data["edit_name"] = " ".join(context.args)
    await update.message.reply_text("Введи новый текст заметки:")
    return EDIT_TEXT


async def edit_get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("edit_name")
    new_text = update.message.text
    result = edit_note(name, new_text)
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


# ====================== КАЛЕНДАРЬ ======================

# ─── Создание события (4 шага) ────────────────────────
async def create_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Название события?")
    return EVENT_NAME

async def create_event_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_name"] = update.message.text.strip()
    await update.message.reply_text("Дата события (ГГГГ-ММ-ДД)?")
    return EVENT_DATE

async def create_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_date"] = update.message.text.strip()
    await update.message.reply_text("Время события (ЧЧ:ММ)?")
    return EVENT_TIME

async def create_event_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event_time"] = update.message.text.strip()
    await update.message.reply_text("Описание события (можно оставить пустым):")
    return EVENT_DETAILS

async def create_event_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("event_name")
    date = context.user_data.get("event_date")
    time = context.user_data.get("event_time")
    details = update.message.text.strip()

    result = calendar.create_event(name, date, time, details)
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


# ─── Чтение, удаление, список (простые команды) ────────
async def read_event_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /readevent <ID>")
        return
    result = calendar.read_event(context.args[0])
    await update.message.reply_text(result)


async def delete_event_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /deleteevent <ID>")
        return
    result = calendar.delete_event(context.args[0])
    await update.message.reply_text(result)


async def list_events_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(calendar.list_events())


# ─── Редактирование события (упрощённо: /editevent <ID>) ──
async def edit_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /editevent <ID>")
        return ConversationHandler.END
    context.user_data["edit_event_id"] = context.args[0]
    await update.message.reply_text(
        "Что хочешь изменить?\n"
        "1 — название\n"
        "2 — дату\n"
        "3 — время\n"
        "4 — описание\n"
        "Напиши цифру:"
    )
    return EDIT_EVENT_FIELD


async def edit_event_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field = update.message.text.strip()
    eid = context.user_data.get("edit_event_id")
    await update.message.reply_text("Введи новое значение:")
    context.user_data["edit_field"] = field
    return EDIT_EVENT_ID   # переиспользуем состояние для значения


async def edit_event_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eid = context.user_data.get("edit_event_id")
    field_map = {"1": "name", "2": "date", "3": "time", "4": "details"}
    field_key = field_map.get(context.user_data.get("edit_field"))

    if not field_key:
        await update.message.reply_text("Неверный выбор.")
        return ConversationHandler.END

    new_value = update.message.text.strip()
    # Для простоты редактируем только одно поле за раз
    result = calendar.edit_event(eid, **{field_key: new_value})
    await update.message.reply_text(result)
    context.user_data.clear()
    return ConversationHandler.END


# ====================== ЗАПУСК БОТА ======================
def main():
    application = Application.builder().token(TOKEN).build()

    # Conversation для создания
    create_conv = ConversationHandler(
        entry_points=[CommandHandler("create", create_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_name)],
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation для редактирования
    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_start)],
        states={
            EDIT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_get_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation для создания события
    event_create_conv = ConversationHandler(
        entry_points=[CommandHandler("createevent", create_event_start)],
        states={
            EVENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_name)],
            EVENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_date)],
            EVENT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_time)],
            EVENT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_details)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation для редактирования события
    event_edit_conv = ConversationHandler(
        entry_points=[CommandHandler("editevent", edit_event_start)],
        states={
            EDIT_EVENT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_field)],
            EDIT_EVENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрация всех обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(create_conv)
    application.add_handler(edit_conv)
    application.add_handler(CommandHandler("read", read_cmd))
    application.add_handler(CommandHandler("delete", delete_cmd))
    application.add_handler(CommandHandler("list", list_short))
    application.add_handler(CommandHandler("listlong", list_long))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(event_create_conv)
    application.add_handler(event_edit_conv)
    application.add_handler(CommandHandler("readevent", read_event_cmd))
    application.add_handler(CommandHandler("deleteevent", delete_event_cmd))
    application.add_handler(CommandHandler("listevents", list_events_cmd))

    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())   # или просто main() если запускать через python -m