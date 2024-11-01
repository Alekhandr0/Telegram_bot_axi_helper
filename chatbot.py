from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.chat_models.gigachat import GigaChat
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import logging
import os

from sympy.codegen.ast import break_


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

        # создание ретривера, ретривер будет возвращать три релевантных документа
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # добавляем историю
        contextualize_q_system_prompt = (
            "Учитывая историю чата и последний вопрос пользователя "
            ", который может ссылаться на контекст в истории чата"
            "сформулируйте отдельный вопрос, который можно понять "
            "без истории чата. НЕ отвечайте на вопрос"
            "- просто переформулируйте его, если нужно, а в противном случае верните как есть."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        system_prompt = (
            "Вы являетесь помощником по поиску ответов на вопросы по документации программного продукта Акси.SCADA компании Акситех. "
            "Используйте следующие фрагменты из извлеченного контекста, чтобы ответить на "
            " вопрос. Если вы не знаете ответа, скажите, что вы "
            "не знаете"
            "\n\n"
            "{context}"
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        combine_docs_chain = create_stuff_documents_chain(llm, qa_prompt)


        self.сhain_history = create_retrieval_chain(history_aware_retriever, combine_docs_chain)


        self.store = {}

        def get_session_history(user_id: str) -> BaseChatMessageHistory:
            if user_id not in self.store:
                self.store[user_id] = ChatMessageHistory()
            return self.store[user_id]

        #создание пайплайна RAG
        self.qa_chain = RunnableWithMessageHistory(
        self.сhain_history,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        )

    def get_response(self, user_id, user_query, chat_history):

            self.logger.info("Инициализация модели GigaChat...")
            self.result = self.qa_chain.invoke({"input": user_query}, config={"configurable": {"session_id": user_id}})
            answer = self.result['answer']
            chat_history = self.result["chat_history"]
            sources = self.result["context"]
            return answer, sources, chat_history

        # очистка истории
    def clear_session_history(self, user_id: str):
        if user_id in self.store:
            self.store[user_id].clear()
