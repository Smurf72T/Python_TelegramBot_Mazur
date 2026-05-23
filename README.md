# Telegram-бот с календарём событий

Многопользовательский Telegram-бот для управления событиями и календарём с веб-панелью администратора.

## 📋 Описание

Проект представляет собой систему для управления событиями через Telegram-бота с возможностью:
- Создания, редактирования и удаления событий
- Публикации событий для других пользователей
- Записи на встречи (appointments)
- Экспорта данных в CSV/JSON форматы
- Веб-административной панели на Django REST Framework

## 🛠 Стек технологий

- **Telegram Bot**: python-telegram-bot v21
- **Backend**: Django 5.0 + Django REST Framework
- **База данных**: PostgreSQL 16
- **Оркестрация**: Docker Compose
- **Тестирование**: pytest + pytest-django

## 👨‍💻 Автор

- **Юрий Мазур**
- GitHub: [Smurf72T](https://github.com/Smurf72T)
- Email: myskk@yandex.ru

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.10+ (для локального запуска)
- Токен Telegram-бота (получить у [@BotFather](https://t.me/BotFather))

### Запуск через Docker (рекомендуется)

1. Скопируйте файл окружения и настройте его:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` и добавьте:
   - `TELEGRAM_BOT_TOKEN` — токен от BotFather
   - `SECRET_KEY` — уникальный секретный ключ для Django (можно сгенерировать случайно)

3. Запустите все сервисы:
   ```bash
   docker-compose up -d
   ```

4. Проверьте логи:
   ```bash
   docker-compose logs -f bot
   docker-compose logs -f django
   ```

### Локальный запуск

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Настройте `.env` (см. выше)

3. Запустите PostgreSQL (локально или через Docker):
   ```bash
   docker-compose up -d db
   ```

4. Примените миграции Django:
   ```bash
   cd django-admin-panel
   python manage.py migrate
   ```

5. Создайте суперпользователя:
   ```bash
   python manage.py createsuperuser
   ```

6. Запустите бота:
   ```bash
   python main.py
   ```

7. Запустите Django сервер (в отдельном терминале):
   ```bash
   cd django-admin-panel
   python manage.py runserver
   ```

## 📱 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Регистрация и приветствие |
| `/help` | Справка по всем командам |
| `/createevent` | Создать новое событие |
| `/editevent` | Редактировать событие |
| `/listevents` | Список всех событий |
| `/readevent` | Просмотр события |
| `/deleteevent` | Удалить событие |
| `/mycalendar` | Мой календарь |
| `/publicevent` | Сделать событие публичным |
| `/publicevents` | Просмотр публичных событий |
| `/appoint` | Создать встречу/приглашение |
| `/myappointments` | Мои встречи (как организатор) |
| `/myinvites` | Приглашения от других |
| `/confirm` | Подтвердить встречу |
| `/decline` | Отклонить встречу |
| `/export` | Экспорт данных (CSV/JSON) |
| `/cancel` | Отменить текущую операцию |

## 🌐 REST API

Доступно через веб-панель администратора:

- `http://localhost:8000/admin/` — Django Admin
- `http://localhost:8000/api/events/` — События
- `http://localhost:8000/api/userprofiles/` — Профили пользователей
- `http://localhost:8000/api/appointments/` — Встречи
- `http://localhost:8000/api/botstatistics/` — Статистика бота (админ)

## 🧪 Тестирование

Запуск тестов через Docker:
```bash
docker-compose up --build tests
```

Или локально:
```bash
pytest
```

## 📁 Структура проекта

```
telegabot/
├── notes_bot/              # Telegram-бот
│   ├── handlers/           # Обработчики команд
│   ├── validators/         # Валидаторы дат/времени
│   ├── utils/              # Утилиты
│   └── *.py                # Менеджеры и бот
├── django-admin-panel/     # Django REST API
│   ├── events/             # Модели и API
│   └── admin_panel/        # Настройки Django
├── shared_utils/           # Общие утилиты
├── tests/                  # Модульные тесты
└── docker-compose.yml      # Оркестрация
```

## 📄 Лицензия

Проект создан для дипломной работы.
