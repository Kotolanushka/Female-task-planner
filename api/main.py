#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain imports
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Female Task Planner API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = "gemini-1.5-flash"

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found! Please check your .env file")

# Initialize AI client
client = ChatGoogleGenerativeAI(
    model=MODEL_ID,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2
)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# Load knowledge base
DOC_PATH = "../Data/Knowledge/productivity.md"
if not os.path.isfile(DOC_PATH):
    raise FileNotFoundError(f"Knowledge base file not found: {DOC_PATH}")

# Load and process documents
loader = TextLoader(DOC_PATH, encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Create vector store
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
retriever = vectorstore.as_retriever()

# Pydantic models
class AdviceIn(BaseModel):
    task: str
    phase: str
    locale: str = "ru"

class AdviceOut(BaseModel):
    verdict: str  # "good", "ok", "avoid"
    reason: str
    suggestion: str

# Helper functions
def docs_to_context(docs):
    """Convert retrieved documents to context string"""
    return "\n".join([doc.page_content for doc in docs])

def pick_system(locale: str) -> str:
    """Select system prompt based on locale"""
    if locale == "ru":
        return """Ты - эксперт по женскому здоровью и менструальному циклу. 
        Анализируй задачи с учетом фазы менструального цикла и давай персональные советы.
        Отвечай на русском языке в формате JSON с полями: verdict, reason, suggestion.
        verdict может быть: "good" (отлично), "ok" (нормально), "avoid" (избегать).
        reason - объяснение почему, suggestion - конкретный совет."""
    else:
        return """You are an expert in women's health and menstrual cycle. 
        Analyze tasks considering menstrual cycle phase and give personalized advice.
        Respond in JSON format with fields: verdict, reason, suggestion.
        verdict can be: "good", "ok", "avoid".
        reason - explanation why, suggestion - specific advice."""

def build_user_prompt(phase: str, task: str, locale: str, context: str) -> str:
    """Build user prompt with phase, task and context"""
    if locale == "ru":
        return f"""Фаза цикла: {phase}
Задача: {task}
Контекст из базы знаний: {context}

Проанализируй эту задачу с учетом фазы менструального цикла и дай совет."""
    else:
        return f"""Cycle phase: {phase}
Task: {task}
Knowledge context: {context}

Analyze this task considering the menstrual cycle phase and give advice."""

# API endpoints
@app.post("/advice", response_model=AdviceOut)
def advice(payload: AdviceIn):
    try:
        # Get relevant context from knowledge base
        ctx = docs_to_context(retriever.get_relevant_documents(payload.task))
        
        # Generate AI response
        resp = client.invoke([
            {"role": "system", "content": pick_system(payload.locale)},
            {"role": "user", "content": build_user_prompt(payload.phase, payload.task, payload.locale, ctx)}
        ])
        
        # Parse response
        raw = resp.content
        try:
            obj = json.loads(raw)
            v = obj.get("verdict", "ok")
            if v not in ("good", "ok", "avoid"): 
                v = "ok"
            return AdviceOut(
                verdict=v, 
                reason=obj.get("reason", ""), 
                suggestion=obj.get("suggestion", "")
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            fallback = {
                "menstruation": ("avoid", "низкая энергия", "перенеси или упрости задачу"),
                "follicular": ("good", "хорошее время для старта", "запланируй первые шаги"),
                "ovulation": ("good", "пик коммуникаций", "назначь встречи/презентации"),
                "luteal": ("ok", "фокус и завершение", "разбей на подзадачи"),
                "unknown": ("ok", "недостаточно данных", "ориентируйся на самочувствие"),
            }
            v, r, s = fallback.get(payload.phase, fallback["unknown"])
            return AdviceOut(verdict=v, reason=r, suggestion=s)
            
    except Exception as e:
        print(f"Error in advice endpoint: {e}")
        # Return fallback response
        fallback = {
            "menstruation": ("avoid", "низкая энергия", "перенеси или упрости задачу"),
            "follicular": ("good", "хорошее время для старта", "запланируй первые шаги"),
            "ovulation": ("good", "пик коммуникаций", "назначь встречи/презентации"),
            "luteal": ("ok", "фокус и завершение", "разбей на подзадачи"),
            "unknown": ("ok", "недостаточно данных", "ориентируйся на самочувствие"),
        }
        v, r, s = fallback.get(payload.phase, fallback["unknown"])
        return AdviceOut(verdict=v, reason=r, suggestion=s)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Female Task Planner API is running"}

@app.get("/")
def root():
    return {"message": "Female Task Planner API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)