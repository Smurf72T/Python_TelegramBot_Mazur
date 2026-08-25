"""
Тесты для обработчиков экспорта данных в Telegram боте.

Тестирует функцию export_callback, которая обрабатывает автоматическое скачивание файлов.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from telegram import Update, CallbackQuery, Message
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from notes_bot.handlers.export_handlers import export_callback


class TestExportCallback:
    """Тесты для функции export_callback."""

    @pytest.mark.asyncio
    async def test_successful_csv_export(self):
        """Тест успешного экспорта в CSV формате."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_document = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data для CSV
        mock_query.data = "export_csv_123456_abc123"
        
        # Мокаем httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.content = b"test,csv,content"
        mock_response.headers = {'content-type': 'text/csv'}
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что файл был отправлен
            mock_query.message.reply_document.assert_called_once()
            call_args = mock_query.message.reply_document.call_args
            assert call_args[1]['filename'].startswith("calendar_123456_")
            assert call_args[1]['filename'].endswith(".csv")
            assert call_args[1]['caption'] == "📁 Ваш календарь в формате CSV"
            assert call_args[1]['document'] == b"test,csv,content"

    @pytest.mark.asyncio
    async def test_successful_json_export(self):
        """Тест успешного экспорта в JSON формате."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_document = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data для JSON
        mock_query.data = "export_json_123456_abc123"
        
        # Мокаем httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.content = b'{"events": []}'
        mock_response.headers = {'content-type': 'application/json'}
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что файл был отправлен
            mock_query.message.reply_document.assert_called_once()
            call_args = mock_query.message.reply_document.call_args
            assert call_args[1]['filename'].startswith("calendar_123456_")
            assert call_args[1]['filename'].endswith(".json")
            assert call_args[1]['caption'] == "📁 Ваш календарь в формате JSON"
            assert call_args[1]['document'] == b'{"events": []}'

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Тест обработки сетевой ошибки."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data
        mock_query.data = "export_csv_123456_abc123"
        
        # Мокаем httpx.RequestError
        import httpx
        mock_error = httpx.RequestError("Network error")
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.side_effect = mock_error
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что отправлено сообщение об ошибке
            mock_query.message.reply_text.assert_called_once()
            call_args = mock_query.message.reply_text.call_args
            assert "Ошибка при подключении к серверу экспорта" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Тест обработки HTTP ошибки."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data
        mock_query.data = "export_csv_123456_abc123"
        
        # Мокаем httpx.HTTPStatusError
        import httpx
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_error = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.side_effect = mock_error
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что отправлено сообщение об ошибке
            mock_query.message.reply_text.assert_called_once()
            call_args = mock_query.message.reply_text.call_args
            assert "Сервер экспорта вернул ошибку 404" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_empty_response_handling(self):
        """Тест обработки пустого ответа от сервера."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data
        mock_query.data = "export_csv_123456_abc123"
        
        # Мокаем httpx.AsyncClient с пустым ответом
        mock_response = MagicMock()
        mock_response.content = b""  # Пустой контент
        mock_response.headers = {'content-type': 'text/csv'}
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что отправлено сообщение об ошибке
            mock_query.message.reply_text.assert_called_once()
            call_args = mock_query.message.reply_text.call_args
            assert "Получен пустой файл от сервера экспорта" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_telegram_error_handling(self):
        """Тест обработки ошибки Telegram при отправке файла."""
        # Создаем моки
        mock_query = MagicMock(spec=CallbackQuery)
        mock_query.message = MagicMock(spec=Message)
        mock_query.message.reply_document = AsyncMock(side_effect=TelegramError("Telegram error"))
        mock_query.message.reply_text = AsyncMock()
        mock_query.answer = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        
        # Настраиваем callback_data
        mock_query.data = "export_csv_123456_abc123"
        
        # Мокаем httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.content = b"test,csv,content"
        mock_response.headers = {'content-type': 'text/csv'}
        
        with patch('notes_bot.handlers.export_handlers.httpx.AsyncClient') as mock_client_class:
            mock_client_instance = AsyncMock()
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client_instance.get.return_value = mock_response
            mock_client_class.return_value = mock_client_instance
            
            # Вызываем тестируемую функцию - она должна обработать исключение и не упасть
            await export_callback(mock_update, mock_context)
            
            # Проверяем, что отправлено сообщение об ошибке Telegram
            mock_query.message.reply_text.assert_called_once()
            call_args = mock_query.message.reply_text.call_args
            assert "Не удалось отправить файл" in call_args[0][0]