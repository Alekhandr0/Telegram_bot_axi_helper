from flask import Flask, request, jsonify
from chatbot import ChatBot
import logging
import json

class WebMessageHandler:
    def __init__(self, chatbot, logger, json_path):
        self.app = Flask(__name__)
        self.chatbot = chatbot
        self.logger = logger
        self.json_path = json_path

        # Загружаем JSON файл
        self.data = self.load_json(json_path)

        # Определяем маршрут для главной страницы
        self.app.add_url_rule('/', 'index', self.index)

        # Определяем маршрут для обработки сообщений
        self.app.add_url_rule('/ask', 'handle_message', self.handle_message, methods=['POST'])

    def index(self):
        """Возвращает HTML-код интерфейса."""
        with open("index.html", "r", encoding='utf-8') as f:
            return f.read()

    def handle_message(self):
        """Обрабатывает запросы от веб-приложения."""
        user_query = request.json.get('query')
        print("user_query - ", user_query)
        # user_id = request.json.get('user_id')  # Получаем ID пользователя из запроса
        user_id = 1555
        self.logger.info(f"Получен запрос от пользователя ID: {user_id}: {user_query}")

        # Получаем историю общения, например, из вашего хранилища или создаем новую
        chat_history = []  # Здесь можно добавить логику получения истории общения

        answer, sources, chat_history = self.chatbot.get_response(user_id, user_query, chat_history)
        
        # Формируем текст ответа и преобразуем объекты `Document` для JSON-сериализации
        response_text = ""
        serialized_sources = []
        for i, doc in enumerate(sources):
            section_tag = doc.metadata.get('section_tag', 'Не указан')
            urls = doc.metadata.get('urls', 'Не указан')
            response_text += f"Источник {i + 1}: Раздел: <a href='{urls}'>{section_tag}</a><br>\n"
            
            # Пробуем использовать атрибут content, если он есть
            serialized_sources.append({
                'section_tag': section_tag,
                'urls': urls
                # 'content': getattr(doc, 'content', 'Контент не доступен')  # заменяем text на content или выводим сообщение
            })


        response = {
            'answer': f'Ответ:  {answer}    Источники:  {response_text}'
        }

        self.logger.info(f"Отправлен ответ пользователю ID: {user_id}: {answer}")
        return jsonify(response)

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

if __name__ == "__main__":
    chatbot = ChatBot()  # Создайте экземпляр вашего бота
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    json_path = "data.json"  # Путь к вашему JSON-файлу с данными

    handler = WebMessageHandler(chatbot, logger, json_path)
    handler.app.run(port=5000)  # Запускаем сервер на порту 
