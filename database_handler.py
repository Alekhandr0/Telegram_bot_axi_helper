import sqlite3

class DatabaseHandler:
    def __init__(self, db_name='chatbot.db'):
        self.db_name = db_name

    def create_connection(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_query TEXT,
            bot_response TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def save_message(self, user_id, user_query, bot_response):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO messages (user_id, user_query, bot_response) VALUES (?, ?, ?)
        ''', (user_id, user_query, bot_response))
        conn.commit()
        conn.close()
