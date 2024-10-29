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
    db_path = r"C:\Programs\Gpt\Test\Telegram_bot\tizi365.db"

    # Инициализация чата и обработчика сообщений
    chatbot = ChatBot(auth, db_path)
    message_handler = MessageHandler(bot_token, chatbot)

    # Запуск бота
    logger.info("Запуск Telegram-бота...")
    try:
        message_handler.start_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main()