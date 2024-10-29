import telebot
from chatbot import ChatBot
import logging

class MessageHandler:
    def __init__(self, bot_token, chatbot):
        self.bot = telebot.TeleBot(bot_token)
        self.chat_history = {}
        self.chatbot = chatbot
        self.logger = logging.getLogger(__name__)

    def handle_message(self, message):
        user_id = message.from_user.id
        user_query = message.text

        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
            self.logger.info(f"Создана новая история общения для пользователя ID: {user_id}")

        self.logger.info(f"Получен запрос от пользователя ID: {user_id}: {user_query}")

        answer, sources = self.chatbot.get_response(user_id, user_query, self.chat_history)
        self.chat_history[user_id].append((user_query, answer))

        self.logger.info(f"Отправлен ответ пользователю ID: {user_id}: {answer}")

        response_text = f"Ответ: {answer}\n\nИсточники:\n"
        for i, source in enumerate(sources):
            section = source.metadata.get("section_tag", "N/A")
            url = source.metadata.get("url", "N/A")
            response_text += f"Источник {i + 1}: Раздел: {section}, URL: {url}\n"

        self.bot.reply_to(message, response_text)

    def start_polling(self):
        self.bot.message_handler(func=lambda message: True)(self.handle_message)
        self.bot.polling(none_stop=True)