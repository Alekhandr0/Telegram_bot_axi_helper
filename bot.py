import logging
from logger_config import setup_logging
from config import get_env
from chatbot import ChatBot
from message_handler import MessageHandler

def main():
    # Настройка логирования
    logger = setup_logging()
    
    # Получение переменных окружения
    env = get_env()
    bot_token = env['telegram_bot_token']
    auth = env['giga_auth']
    db_path = r".\tizi365.db"
    json_path= r".\response_db.json"

    # Инициализация чата и обработчика сообщений
    chatbot = ChatBot(auth, db_path, logger)
    message_handler = MessageHandler(bot_token, chatbot, logger, json_path)

    # Запуск бота
    logger.info("Запуск Telegram-бота...")
    try:
        message_handler.start_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()