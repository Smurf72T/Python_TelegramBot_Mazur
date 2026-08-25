from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

# Загружаем переменные окружения ПЕРЕД любыми импортами
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import django

# Настраиваем Django-окружение (только один раз)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DJANGO_PATH = os.path.join(BASE_DIR, 'django-admin-panel')
sys.path.insert(0, DJANGO_PATH)

# Ожидание готовности базы данных (после загрузки .env)
from shared_utils.db_utils import wait_for_db

# Импортируем обработчики команд из соответствующих модулей
from notes_bot.handlers.main_handlers import start, register, cancel, handle_help
from notes_bot.handlers.event_handlers import (
    create_start, create_name, create_date, create_time, create_details,
    read_event, delete_event, edit_start, edit_choose_field, edit_set_value, list_events
)
from notes_bot.handlers.appointment_handlers import (
    appoint_start, appoint_details, appoint_skip, my_appointments, my_invites,
    confirm_appointment, decline_appointment
)
from notes_bot.handlers.calendar_handlers import (
    my_calendar, toggle_public_event, public_events
)
from notes_bot.handlers.export_handlers import export_menu, export_callback

# Ожидаем готовности базы данных в Docker-режиме
if os.getenv('RUN_ENV') == 'docker':
    print("Docker-режим: ожидание готовности базы данных...")
    wait_for_db()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from notes_bot.calendar_functions import Calendar

try:
    from secrets import TOKEN
except ImportError:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Токен не найден")

# Состояния
NAME, DATE, TIME, DETAILS = range(4)
EDIT_FIELD, EDIT_VALUE = range(2)
APPOINT_COMMENT = 0

# Вспомогательные функции перенесены в notes_bot.utils.helpers

def main():
    calendar = Calendar()

    application = Application.builder() \
        .token(TOKEN) \
        .connection_pool_size(10) \
        .get_updates_connection_pool_size(10) \
        .read_timeout(30) \
        .write_timeout(30) \
        .connect_timeout(30) \
        .pool_timeout(30) \
        .build()

    application.bot_data["calendar"] = calendar

    create_conv = ConversationHandler(
        entry_points=[CommandHandler("createevent", create_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_name)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_time)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_details)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("editevent", edit_start)],
        states={
            EDIT_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_choose_field)],
            EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_set_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    appoint_conv = ConversationHandler(
        entry_points=[CommandHandler("appoint", appoint_start)],
        states={
            APPOINT_COMMENT: [
                CommandHandler("skip", appoint_skip),
                MessageHandler(filters.TEXT & ~filters.COMMAND, appoint_details),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(create_conv)
    application.add_handler(edit_conv)
    application.add_handler(CommandHandler("listevents", list_events))
    application.add_handler(CommandHandler("readevent", read_event))
    application.add_handler(CommandHandler("deleteevent", delete_event))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(appoint_conv)
    application.add_handler(CommandHandler("myappointments", my_appointments))
    application.add_handler(CommandHandler("myinvites", my_invites))
    application.add_handler(CommandHandler("confirm", confirm_appointment))
    application.add_handler(CommandHandler("decline", decline_appointment))
    application.add_handler(CommandHandler("mycalendar", my_calendar))
    application.add_handler(CommandHandler("publicevent", toggle_public_event))
    application.add_handler(CommandHandler("publicevents", public_events))
    application.add_handler(CommandHandler("export", export_menu))
    application.add_handler(CallbackQueryHandler(export_callback, pattern='^export_(csv|json)_'))

    print("Многопользовательский Календарь-бот запущен...")

    try:
        # Создаём event loop для Python 3.14+
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        calendar.close()


if __name__ == "__main__":
    main()