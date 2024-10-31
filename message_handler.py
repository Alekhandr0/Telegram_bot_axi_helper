import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from chatbot import ChatBot
import logging
from telebot.types import InputMediaPhoto
import json
from database_handler import DatabaseHandler  # Импортируем наш класс

class MessageHandler:
    def __init__(self, bot_token, chatbot, logger, json_path):
        self.bot = telebot.TeleBot(bot_token)
        self.chat_history = {}
        self.chatbot = chatbot
        self.logger = logger
        self.first_message_received = {}  # Словарь для отслеживания первого сообщения
        self.db_handler = DatabaseHandler()  # Инициализируем класс для работы с БД
                # Загружаем JSON файл
        self.data = self.load_json(json_path)

    def load_json(self, path):
        """Загружает данные из JSON-файла."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_data_by_id(self, id):
        """Находит запись в JSON по заданному id."""
        for entry in self.data:
            if entry.get("id") == id:
                return entry
        return None  # Возвращаем None, если запись не найдена


    def send_welcome_message(self, user_id, chat_id):
        welcome_message = "Привет, я ИИ помощник, который будет тебе помогать с продуктами Акситеха."
        self.bot.send_message(chat_id, welcome_message)
        self.logger.info(f"Отправлено приветственное сообщение пользователю ID: {user_id}")

    def send_multiple_photos_with_text(self, chat_id, text, photos, url_doc, reply_markup):
            """
            Отправляет несколько фото в одном сообщении с текстом и URL документа.
            """
            media_group = [InputMediaPhoto(open(photo, 'rb')) for photo in photos]
            
            # Добавляем текст к первому фото, если он задан
            if media_group:
                media_group[0].caption = f"{text}"
            
            # Отправляем альбом фото
            self.bot.send_media_group(chat_id, media_group)
            # Отправляем клавиатуру отдельно после альбома
            self.bot.send_message(chat_id, text=f"Ссылка на документ:{url_doc}", reply_markup=reply_markup)

    def create_keyboard(self, faq_mode=False):
        """
        Создает клавиатуру.
        Если faq_mode=True, то добавляются кнопки для режима FAQ.
        """
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        
        if faq_mode:
            # Кнопки для режима FAQ
            back_button = KeyboardButton("Назад")
            option1_button = KeyboardButton("1")
            option2_button = KeyboardButton("2")
            option3_button = KeyboardButton("3")
            option4_button = KeyboardButton("4")
            option5_button = KeyboardButton("5")
            option6_button = KeyboardButton("6")
            markup.add(back_button, option1_button, option2_button, option3_button, option4_button, option5_button, option6_button)
        else:
            # Основные кнопки
            clear_button = KeyboardButton("Очистить историю")
            faq_button = KeyboardButton("Часто задаваемые вопросы")
            help_button = KeyboardButton("Помощь")
            contact_button = KeyboardButton("Контактная информация")
            markup.add(clear_button, faq_button, help_button, contact_button)
        
        return markup


    def handle_message(self, message):
        user_id = message.from_user.id
        user_query = message.text

        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
            self.logger.info(f"Создана новая история общения для пользователя ID: {user_id}")
            
            # Отправляем приветственное сообщение только при первом запросе
            if user_id not in self.first_message_received:
                self.send_welcome_message(user_id, message.chat.id)
                self.first_message_received[user_id] = True  # Устанавливаем флаг о первом сообщении
                return  # Завершаем выполнение, не обрабатывая основной запрос

        # Проверяем, не нажал ли пользователь кнопку "Очистить историю"
        if user_query == "Очистить историю":
            self.chat_history[user_id] = []
            self.logger.info(f"История общения очищена для пользователя ID: {user_id}")
            response_text = "Ваша история общения была очищена."
            reply_markup = self.create_keyboard()

        elif user_query == "Помощь":
            response_text = "Я могу ответить на вопросы по продуктам Акситеха. Задайте вопрос, и я постараюсь помочь!"
            reply_markup = self.create_keyboard()

        elif user_query == "Контактная информация":
            response_text = "Для связи с поддержкой, напишите на support@axitech.com."
            reply_markup = self.create_keyboard()

        elif user_query == "Часто задаваемые вопросы":
            response_text = "Выберите вопрос, на который хотите получить ответ, или вернитесь назад. \n 1) Как настроить визуализацию на портале \"Диспетчерская\"? \n 2) Как настроить панель на главной странице? \n 3) Как настраивать и изменять фильтры по событиям? \n 4) Как настраивать вид таблицы и применять фильтры? \n 5) Как настраивать вид графиков? \n 6) Как настраивать карту и применять к ней фильтры?"
            reply_markup = self.create_keyboard(faq_mode=True)  # Переход в режим FAQ

        elif user_query == "Назад":
            response_text = "Вы вернулись в основное меню."
            reply_markup = self.create_keyboard()  # Возвращаемся в основное меню

        elif user_query == "1"  or user_query == "2" or user_query == "3" or user_query == "4" or user_query == "5" or user_query == "6" :
            faq_data = self.get_data_by_id(user_query)
            if faq_data:
                response_text = faq_data["message"]
                photos = faq_data["media_group"]
                url_doc = faq_data["url"]
                reply_markup = self.create_keyboard(faq_mode=True)
                self.send_multiple_photos_with_text(message.chat.id, response_text, photos, url_doc, reply_markup)
                return
            else:
                response_text = "Извините, информация по данному вопросу не найдена."
                reply_markup = self.create_keyboard()

        

        else:
            # Обработка пользовательских запросов, как и раньше
            self.logger.info(f"Получен запрос от пользователя ID: {user_id}: {user_query}")
            answer, sources = self.chatbot.get_response(user_id, user_query, self.chat_history)
            self.chat_history[user_id].append((user_query, answer))

            # Сохраняем запрос и ответ в базе данных
            self.db_handler.save_message(user_id, user_query, answer)
            
            self.logger.info(f"Отправлен ответ пользователю ID: {user_id}: {answer}")
            response_text = f"Ответ: {answer}\n\nИсточники:\n"
            for i, source in enumerate(sources):
                section = source.metadata.get("section_tag", "N/A")
                url = source.metadata.get("url", "N/A")
                response_text += f"Источник {i + 1}: Раздел: {section}, URL: {url}\n"
            
            reply_markup = self.create_keyboard()
            self.bot.reply_to(message, response_text, reply_markup=reply_markup)
            return  # Завершаем выполнение, чтобы не вызывался `self.send_text_with_photo`

        # Отправляем текст с фото или без
        self.bot.reply_to(message, response_text, reply_markup=reply_markup)


    def start_polling(self):
        self.bot.message_handler(func=lambda message: True)(self.handle_message)
        self.bot.polling(none_stop=True)
