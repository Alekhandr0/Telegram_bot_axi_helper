from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain_community.chat_models.gigachat import GigaChat
from langchain_chroma import Chroma
import logging
import os

class ChatBot:
    def __init__(self, auth, db_path, logger):
        self.logger = logger
        # self.logger.info("Инициализация модели GigaChat...")
        
        self.llm = GigaChat(credentials=auth, scope="GIGACHAT_API_PERS", model="GigaChat", verify_ssl_certs=False)
        self.vectorstore = Chroma(
            collection_name="my_collection",
            embedding_function=GigaChatEmbeddings(credentials=auth, verify_ssl_certs=False),
            persist_directory=db_path,
        )
        self.retriever = self.vectorstore.as_retriever()
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            retriever=self.retriever,
            llm=self.llm,
            return_source_documents=True,
        )

    def get_response(self, user_id, user_query, chat_history):
        self.logger.info("Инициализация модели GigaChat...")
        result = self.qa_chain.invoke({"chat_history": chat_history[user_id], "question": user_query})
        answer = result.get("result") or result.get("answer")
        sources = result["source_documents"]
        return answer, sources