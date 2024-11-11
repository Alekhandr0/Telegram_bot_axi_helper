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

    def send_multiple_photos_with_text(self, chat_id, text, photos, url_doc, type_question_text, question_text ,reply_markup):
            """
            Отправляет несколько фото в одном сообщении с текстом и URL документа.
            """
            media_group = [InputMediaPhoto(open(photo, 'rb')) for photo in photos]
            
            # Добавляем текст к первому фото, если он задан
            if media_group:
                media_group[0].caption = f"{question_text} \n {text}"
            
            if len(media_group)>0:
                # Отправляем альбом фото
                self.bot.send_media_group(chat_id, media_group)
                # Отправляем клавиатуру отдельно после альбома
            else:
                self.bot.send_message(chat_id, text=f"{question_text} \n {text}")    

            self.bot.send_message(chat_id, text=f"Ссылка на документ:{url_doc}", reply_markup=reply_markup)

    def create_keyboard(self, faq_mode=False, type_port=0):
        """
        Создает клавиатуру.
        Если faq_mode=True, то добавляются кнопки для режима FAQ.
        """
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        
        if faq_mode:
            if type_port==0:
                back_main = KeyboardButton("Главное меню")  #Диспетчерская Конфигуратор Управление доступом
                dispetch =  KeyboardButton("Диспетчерская")
                konfig =  KeyboardButton("Конфигуратор")
                uprl_dost =  KeyboardButton("Управление доступом")
                markup.add(back_main, dispetch, konfig, uprl_dost)
            elif type_port==1:
            # Кнопки для режима Диспетчерская
                back_main = KeyboardButton("Главное меню")
                back_button = KeyboardButton("Назад")
                option1_button = KeyboardButton("11")
                option2_button = KeyboardButton("12")
                option3_button = KeyboardButton("13")
                option4_button = KeyboardButton("14")
                option5_button = KeyboardButton("15")
                option6_button = KeyboardButton("16")
                option7_button = KeyboardButton("17")
                option8_button = KeyboardButton("18")
                option9_button = KeyboardButton("19")
                markup.add(back_main, back_button, option1_button, option2_button, option3_button, option4_button, option5_button, option6_button, option7_button, option8_button, option9_button)
            elif type_port==2:
            # Кнопки для режима Конфигуратор
                back_main = KeyboardButton("Главное меню")
                back_button = KeyboardButton("Назад")
                option21_button = KeyboardButton("21")
                option22_button = KeyboardButton("22")
                option23_button = KeyboardButton("23")
                option24_button = KeyboardButton("24")
                option25_button = KeyboardButton("25")
                option26_button = KeyboardButton("26")
                markup.add(back_main, back_button, option21_button, option22_button, option23_button, option24_button, option25_button, option26_button)

            elif type_port==3:
            # Кнопки для режима Диспетчерская
                back_main = KeyboardButton("Главное меню")
                back_button = KeyboardButton("Назад")
                option31_button = KeyboardButton("31")
                option32_button = KeyboardButton("32")
                option33_button = KeyboardButton("33")
                option34_button = KeyboardButton("34")
                option35_button = KeyboardButton("35")
                option36_button = KeyboardButton("36")
                option37_button = KeyboardButton("37")
                option38_button = KeyboardButton("38")
                markup.add(back_main, back_button, option31_button, option32_button, option33_button, option34_button, option35_button, option36_button, option37_button, option38_button)
            
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
        id_question = [str(item["id"]) for item in self.data]

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
            self.chatbot.clear_chat_history()
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
            response_text = "Выберите раздел который вас интресует"
            reply_markup = self.create_keyboard(faq_mode=True)  # Переход в режим FAQ

        elif user_query == "Назад":
            response_text = "Вы вернулись в раздел с часто задаваемыми вопросами, тут можно выбрать портал."
            reply_markup = self.create_keyboard(faq_mode=True)  # Возвращаемся в основное меню
            
            # Главное меню
        
        elif user_query == "Главное меню":
            response_text = "Вы вернулись на Главное меню."
            reply_markup = self.create_keyboard()  # Возвращаемся в основное меню

        elif str(user_query) in id_question:
            faq_data = self.get_data_by_id(user_query)
            if faq_data:
                response_text = faq_data["message"]
                photos = faq_data["media_group"]
                url_doc = faq_data["url"]
                type_question_text =  faq_data["type_question"]
                question_text = faq_data["question"]
                reply_markup = self.create_keyboard(faq_mode=True,type_port=int(user_query)//10)
                self.send_multiple_photos_with_text(message.chat.id, response_text, photos, url_doc, type_question_text, question_text, reply_markup)
                return
            else:
                response_text = "Извините, информация по данному вопросу не найдена."
                reply_markup = self.create_keyboard()

        elif user_query == "Диспетчерская":
            response_text = "Часто задаваемые вопросы по порталу \"Диспетчерская\": \n11) Как настроить визуализацию на портале \"Диспетчерская\"?\n12) Как настроить панель на главной странице?\n13) Как настраивать и изменять фильтры по событиям?\n14) Как настраивать вид таблицы и применять фильтры?\n15) Как настраивать вид графиков?\n16) Как настраивать карту и применять к ней фильтры?\n17) Как создавать отчеты?\n18) Как создавать графики в отчетах?\n19) Как добавлять и редактировать список контактов для рассылки?"
            reply_markup = self.create_keyboard(faq_mode=True, type_port=1)  # Переход на вопросы по диспетчерской

        elif user_query == "Конфигуратор":
            response_text = "Часто задаваемые вопросы по порталу \"Конфигуратор\" \n21) Как настроить оборудование систем телеметрии для передачи данных на пульт управления?\n22) Как удалить параметр из объекта?\n23) Как связать параметр с объектом?\n24) Можно ли использовать один драйвер для нескольких объектов?\n25) Как влияет изменение адресации на привязку параметров к устройству?\n26) Как перезапустить драйвер?"
            reply_markup = self.create_keyboard(faq_mode=True, type_port=2)  # Переход на вопросы по Конфигуратор

        elif user_query == "Управление доступом":
            response_text = "Часто задаваемые вопросы по порталу \"Управление доступом\" \n31) Как создать новый аккаунт?\n32) Как редактировать информацию об аккаунте?\n33) Какие правила доступа можно установить для пользователей?\n34) Как создать пользователей с необходимыми ролями?\n35) Как создать пользователей с необходимыми ролями?\n36) Как настроить доступ к системе с использованием RBAC и ABAC в Акси.SCADA?\n37) Как создать новый профиль\n38) Можно ли создавать собственные роли пользователей?"
            reply_markup = self.create_keyboard(faq_mode=True, type_port=3)  # Переход на вопросы по Управление доступом    

        else:
            # Обработка пользовательских запросов, как и раньше
            self.logger.info(f"Получен запрос от пользователя ID: {user_id}: {user_query}")
            answer, sources, chat_history = self.chatbot.get_response(user_id, user_query, self.chat_history)


            # Сохраняем запрос и ответ в базе данных
            self.db_handler.save_message(user_id, user_query, answer)
            
            self.logger.info(f"Отправлен ответ пользователю ID: {user_id}: {answer}")

            response_text = f"Ответ: {answer}\n\nИсточники:\n"
            print(chat_history)
            for i, doc in enumerate(sources):
                section_tag = doc.metadata.get('section_tag')
                urls = doc.metadata.get('urls')
                response_text += f"Источник {i + 1}: Раздел: {section_tag}, URL: {urls}\n"

            
            reply_markup = self.create_keyboard()
            self.bot.reply_to(message, response_text, parse_mode='Markdown', reply_markup=reply_markup)
            return  # Завершаем выполнение, чтобы не вызывался `self.send_text_with_photo`

        # Отправляем текст с фото или без
        self.bot.reply_to(message, response_text, reply_markup=reply_markup)


    def start_polling(self):
        self.bot.message_handler(func=lambda message: True)(self.handle_message)
        self.bot.polling(none_stop=True)
