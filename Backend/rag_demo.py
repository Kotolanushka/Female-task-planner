#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma

# Google Gemini imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# ----------------------------
# 1️⃣ Загружаем переменные из .env
# ----------------------------
load_dotenv()  # ищет файл .env в текущей директории
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY не найден! Проверь файл .env")

# ----------------------------
# 2️⃣ Путь к Markdown с базой знаний
# ----------------------------
DOC_PATH = "../Data/Knowledge/productivity.md"

if not os.path.isfile(DOC_PATH):
    raise FileNotFoundError(f"Файл с базой знаний не найден: {DOC_PATH}")

# ----------------------------
# 3️⃣ Загружаем документ
# ----------------------------
loader = TextLoader(DOC_PATH, encoding="utf-8")
documents = loader.load()

# ----------------------------
# 4️⃣ Разбиваем документ на куски для векторизации
# ----------------------------
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# ----------------------------
# 5️⃣ Создаём эмбеддинги и Chroma векторное хранилище
# ----------------------------
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")

# ----------------------------
# 6️⃣ Настраиваем RetrievalQA
# ----------------------------
retriever = vectorstore.as_retriever()
qa = RetrievalQA.from_chain_type(
    llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0),
    retriever=retriever
)

# ----------------------------
# 7️⃣ Цикл вопросов от пользователя
# ----------------------------
print("🤖 Female Task Planner AI (Gemini) запущен! Введи вопрос (или 'exit' для выхода).")

while True:
    query = input("\nТвой вопрос: ")
    if query.lower() in ["exit", "quit", "выход"]:
        print("👋 Выход. До встречи!")
        break
    try:
        answer = qa.run(query)
        print(f"\nAI совет: {answer}")
    except Exception as e:
        print(f"Ошибка при получении ответа: {e}")
