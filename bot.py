import logging
import threading
from logger_config import setup_logging
from config import get_env
from chatbot import ChatBot
from message_handler import MessageHandler
from web_message_handler import WebMessageHandler

def start_telegram_bot(message_handler, logger):
    logger.info("Запуск Telegram-бота...")
    try:
        message_handler.start_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

def start_web_app(web_message_handler, logger):
    logger.info("Запуск веб-приложения...")
    try:
        web_message_handler.app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Ошибка при запуске веб-приложения: {e}")

def main():
    # Настройка логирования
    logger = setup_logging()
    
    # Получение переменных окружения
    env = get_env()
    bot_token = env['telegram_bot_token']
    auth_llm = env['giga_auth_llm']
    auth_embed = env['giga_auth_embed']
    weaviate_url = env['weaviate_url']
    weaviate_api_key = env['weaviate_api_key']
    db_path = r".\tizi365.db"
    json_path = r".\response_db.json"

    # Инициализация чата и обработчиков сообщений
    chatbot = ChatBot(weaviate_url, weaviate_api_key, auth_llm, auth_embed, db_path, logger)
    message_handler = MessageHandler(bot_token, chatbot, logger, json_path)
    web_message_handler = WebMessageHandler(chatbot, logger, json_path)

    # Создание потоков для запуска Telegram-бота и веб-приложения
    bot_thread = threading.Thread(target=start_telegram_bot, args=(message_handler, logger))
    web_thread = threading.Thread(target=start_web_app, args=(web_message_handler, logger))

    # Запуск потоков
    bot_thread.start()
    web_thread.start()

    # Ожидание завершения потоков
    bot_thread.join()
    web_thread.join()

if __name__ == "__main__":
    main()
