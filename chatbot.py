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
from langchain_core.runnables import RunnablePassthrough
from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate
from dotenv import load_dotenv
from sympy.abc import alpha
from weaviate.classes.init import Auth
import logging
import os

from sympy.codegen.ast import break_


class ChatBot:
    def __init__(self, weaviate_url, weaviate_api_key, auth_llm, auth_embed, db_path, logger):
        self.logger = logger
        # self.logger.info("Инициализация модели GigaChat...")
        
        llm = GigaChat(credentials=auth_llm, scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)

        client = weaviate.connect_to_local()

        vectorstore = WeaviateVectorStore(
            client=client,
            index_name="AxiSCADA",
            text_key="documents",
            embedding=GigaChatEmbeddings(
                credentials=auth_embed,
                verify_ssl_certs=False)
        )


        # создание ретривера, ретривер будет возвращать 4 релевантных документа. С помощью alpha можно регулировать веса поиска (семантический
        # и по ключевым словам). Алгоритмы в основе - cosine similarity и BM25.
        retriever = vectorstore.as_retriever(search_type='similarity', search_kwargs={"k": 4, "alpha": 0.5})

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

        #Предыдущий метод хранения истории сообщений , пока не удаляю
        # self.store = {}
        #
        # def get_chat_history(user_id: str) -> BaseChatMessageHistory:
        #     if user_id not in self.store:
        #         self.store[user_id] = ChatMessageHistory()
        #     return self.store[user_id]

        self.get_session_history = ChatMessageHistory()

        # Функция отвечает за обрезку истории
        def trim_messages(chain_input):
            stored_messages = self.get_session_history.messages
            if len(stored_messages) <= 4:
                return False
            self.get_session_history.clear()

            #Цикл отвечает за хранение последних двух сообщений в истории. Если история не нужна , необходимо закомментировать
            for message in stored_messages[-2:]:
                self.get_session_history.add_message(message)

            return True

        #создание пайплайна RAG
        self.qa_chain = RunnableWithMessageHistory(
        self.сhain_history,
        lambda session_id: self.get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        )

        #Донастройка пайплайна
        self.chain_with_trimming = (
            RunnablePassthrough.assign(messages_trimmed=trim_messages)
            | self.qa_chain
            )
    def get_response(self, user_id, user_query, chat_history):

            self.logger.info("Инициализация модели GigaChat...")
            self.result = self.chain_with_trimming.invoke({"input": user_query}, config={"configurable": {"session_id": user_id}})
            answer = self.result['answer']
            chat_history = self.result["chat_history"]
            sources = self.result["context"]
            return answer, sources, chat_history

        # очистка истории
    def clear_chat_history(self):
            self.get_session_history.clear()
