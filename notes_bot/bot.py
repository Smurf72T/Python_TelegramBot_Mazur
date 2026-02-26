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
        "/cancel — отменить текущее действие"
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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(create_conv)
    application.add_handler(edit_conv)
    application.add_handler(CommandHandler("read", read_cmd))
    application.add_handler(CommandHandler("delete", delete_cmd))
    application.add_handler(CommandHandler("list", list_short))
    application.add_handler(CommandHandler("listlong", list_long))
    application.add_handler(CommandHandler("cancel", cancel))

    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.run(main())   # или просто main() если запускать через python -m