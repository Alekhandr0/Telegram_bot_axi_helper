from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.chat_models.gigachat import GigaChat
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
import logging
import os

class ChatBot:
    def __init__(self, auth, db_path, logger):
        self.logger = logger
        # self.logger.info("Инициализация модели GigaChat...")
        
        llm = GigaChat(credentials=auth, scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)
        vectorstore = Chroma(
            collection_name="my_collection",
            embedding_function=GigaChatEmbeddings(credentials=auth, verify_ssl_certs=False),
            persist_directory=db_path,
        )
        #используем архитектуру фреймворка Langchain
        #шаблон промпта
        template = """
        Отвечай по русски. Не выдумывай. Используя только следующий контекст, ответьте на вопрос:
        Вопрос: {input}

        <context>
        {context}
        </context>

        Источники:
        {{sources}}
        """
        #создание промпта
        prompt = (PromptTemplate(
        input_variables = ["input", "context"],
        template = template)
        )

        #создание ретривера, ретривер будет возвращать три релевантных документа
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        #передаем в нашу модель набор документов
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)

        #создание пайплайна RAG
        self.qa_chain = create_retrieval_chain(
        retriever, combine_docs_chain
        )

    def get_response(self, user_id, user_query, chat_history):
        self.logger.info("Инициализация модели GigaChat...")

        self.result = self.qa_chain.invoke({"input": user_query})
        answer = self.result.get("answer")

        sources = self.result["context"]
        return answer, sources