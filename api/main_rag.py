#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Female Task Planner RAG API", 
    version="2.0.0",
    description="RAG-powered task planner for women with menstrual cycle analysis"
)

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

if not GOOGLE_API_KEY:
    print("⚠️  GOOGLE_API_KEY not found! Using fallback mode.")
    model = None
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Google Gemini configured successfully")
    except Exception as e:
        print(f"⚠️  Error configuring Gemini: {e}")
        model = None

# Pydantic models
class AdviceIn(BaseModel):
    task: str
    phase: str
    locale: str = "ru"

class AdviceOut(BaseModel):
    verdict: str  # "good", "ok", "avoid"
    reason: str
    suggestion: str
    confidence: float = 0.0
    source: str = "fallback"

class DocumentSearch(BaseModel):
    query: str
    limit: int = 3

class DocumentOut(BaseModel):
    content: str
    relevance_score: float
    source: str

# RAG Knowledge Base - Structured data for better retrieval
RAG_KNOWLEDGE_BASE = {
    "menstruation": {
        "phase_info": {
            "days": "1-5",
            "description": "Менструация - начало цикла",
            "hormones": "низкий эстроген, низкий прогестерон"
        },
        "physical_effects": [
            "низкая энергия",
            "усталость",
            "возможны спазмы",
            "снижение выносливости",
            "повышенная чувствительность к боли"
        ],
        "cognitive_effects": [
            "снижение концентрации",
            "замедленная реакция",
            "повышенная раздражительность",
            "сложности с принятием решений"
        ],
        "productivity_tips": [
            "планируйте легкие задачи",
            "избегайте важных встреч",
            "делайте больше перерывов",
            "делегируйте сложные задачи"
        ],
        "task_recommendations": {
            "good": ["отдых", "планирование", "анализ данных"],
            "ok": ["рутинные задачи", "административная работа"],
            "avoid": ["важные презентации", "сложные переговоры", "интенсивная работа"]
        }
    },
    "follicular": {
        "phase_info": {
            "days": "6-10",
            "description": "Фолликулярная фаза - рост фолликулов",
            "hormones": "растущий эстроген"
        },
        "physical_effects": [
            "повышение энергии",
            "улучшение настроения",
            "повышение мотивации",
            "лучшее самочувствие"
        ],
        "cognitive_effects": [
            "улучшение концентрации",
            "повышение креативности",
            "лучшая память",
            "усиленная мотивация к обучению"
        ],
        "productivity_tips": [
            "идеальное время для новых проектов",
            "планируйте важные задачи",
            "занимайтесь обучением",
            "начинайте новые инициативы"
        ],
        "task_recommendations": {
            "good": ["планирование", "обучение", "творческие задачи", "новые проекты"],
            "ok": ["аналитическая работа", "исследования", "разработка стратегий"],
            "avoid": ["рутинные задачи", "повторяющаяся работа"]
        }
    },
    "ovulation": {
        "phase_info": {
            "days": "11-15",
            "description": "Овуляция - выход яйцеклетки",
            "hormones": "пик эстрогена, выброс ЛГ"
        },
        "physical_effects": [
            "пик энергии",
            "максимальная выносливость",
            "повышенная уверенность",
            "лучшая координация"
        ],
        "cognitive_effects": [
            "максимальная концентрация",
            "лучшая коммуникабельность",
            "повышенная уверенность",
            "эффективное принятие решений"
        ],
        "productivity_tips": [
            "идеальное время для важных встреч",
            "планируйте презентации",
            "проводите переговоры",
            "занимайтесь лидерскими задачами"
        ],
        "task_recommendations": {
            "good": ["презентации", "встречи", "переговоры", "лидерские задачи"],
            "ok": ["командная работа", "социальные активности", "сетевые мероприятия"],
            "avoid": ["одиночная работа", "рутинные задачи"]
        }
    },
    "luteal": {
        "phase_info": {
            "days": "16-28",
            "description": "Лютеальная фаза - подготовка к менструации",
            "hormones": "высокий прогестерон, снижение эстрогена"
        },
        "physical_effects": [
            "снижение энергии",
            "возможные перепады настроения",
            "повышенная чувствительность",
            "возможные головные боли"
        ],
        "cognitive_effects": [
            "снижение концентрации",
            "повышенная критичность",
            "лучшие аналитические способности",
            "повышенное внимание к деталям"
        ],
        "productivity_tips": [
            "фокусируйтесь на завершении проектов",
            "делайте детальную работу",
            "планируйте на будущее",
            "делегируйте новые задачи"
        ],
        "task_recommendations": {
            "good": ["завершение проектов", "детальная работа", "анализ", "планирование"],
            "ok": ["административные задачи", "отчетность", "организация"],
            "avoid": ["новые проекты", "важные презентации", "сложные переговоры"]
        }
    }
}

def search_knowledge_base(query: str, phase: str, limit: int = 3) -> List[dict]:
    """RAG: Retrieve relevant information from knowledge base"""
    phase_data = RAG_KNOWLEDGE_BASE.get(phase, {})
    
    # Simple keyword-based retrieval
    query_lower = query.lower()
    results = []
    
    # Search in different sections
    for section, content in phase_data.items():
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, list):
                    for item in value:
                        if any(word in item.lower() for word in query_lower.split()):
                            results.append({
                                "content": item,
                                "section": section,
                                "key": key,
                                "relevance_score": 0.8
                            })
                elif isinstance(value, str) and any(word in value.lower() for word in query_lower.split()):
                    results.append({
                        "content": value,
                        "section": section,
                        "key": key,
                        "relevance_score": 0.9
                    })
    
    # Sort by relevance and return top results
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:limit]

def generate_rag_advice(task: str, phase: str, locale: str) -> dict:
    """RAG: Generate advice using retrieved context"""
    # Step 1: Retrieve relevant information
    retrieved_docs = search_knowledge_base(task, phase, limit=3)
    
    # Step 2: Build context from retrieved documents
    context = f"Фаза цикла: {phase}\n"
    context += f"Задача: {task}\n\n"
    context += "Ретривленная информация:\n"
    
    for i, doc in enumerate(retrieved_docs, 1):
        context += f"{i}. {doc['content']} (из {doc['section']})\n"
    
    # Step 3: Generate advice using AI or fallback
    if model and GOOGLE_API_KEY:
        try:
            prompt = f"""Ты - эксперт по женскому здоровью и менструальному циклу.

{context}

На основе ретривленной информации проанализируй задачу и дай персональный совет.

Отвечай в формате JSON:
{{"verdict": "good/ok/avoid", "reason": "объяснение", "suggestion": "конкретный совет", "confidence": 0.8}}"""

            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            return {
                "verdict": result.get("verdict", "ok"),
                "reason": result.get("reason", ""),
                "suggestion": result.get("suggestion", ""),
                "confidence": float(result.get("confidence", 0.8)),
                "source": "rag_ai"
            }
        except Exception as e:
            print(f"RAG AI Error: {e}")
            return generate_fallback_advice(task, phase, locale, retrieved_docs)
    else:
        return generate_fallback_advice(task, phase, locale, retrieved_docs)

def generate_fallback_advice(task: str, phase: str, locale: str, retrieved_docs: List[dict] = None) -> dict:
    """Fallback advice generation using retrieved context"""
    phase_data = RAG_KNOWLEDGE_BASE.get(phase, {})
    task_recommendations = phase_data.get("task_recommendations", {})
    
    # Simple keyword matching for verdict
    task_lower = task.lower()
    verdict = "ok"
    
    for rec_type, tasks in task_recommendations.items():
        if any(keyword in task_lower for keyword in tasks):
            verdict = rec_type
            break
    
    # Generate reason and suggestion based on retrieved docs
    if retrieved_docs:
        reason = retrieved_docs[0]["content"] if retrieved_docs else "анализ фазы цикла"
        suggestion = f"Учитывая {phase} фазу: {retrieved_docs[0]['content']}" if retrieved_docs else "ориентируйтесь на самочувствие"
    else:
        fallback_reasons = {
            "menstruation": "низкая энергия",
            "follicular": "хорошее время для старта", 
            "ovulation": "пик коммуникаций",
            "luteal": "фокус на завершении"
        }
        reason = fallback_reasons.get(phase, "анализ фазы цикла")
        suggestion = f"Учитывая {phase} фазу: {reason}"
    
    return {
        "verdict": verdict,
        "reason": reason,
        "suggestion": suggestion,
        "confidence": 0.6,
        "source": "rag_fallback"
    }

# API endpoints
@app.post("/advice", response_model=AdviceOut)
def advice(payload: AdviceIn):
    """RAG-powered advice endpoint"""
    try:
        advice_data = generate_rag_advice(payload.task, payload.phase, payload.locale)
        return AdviceOut(**advice_data)
    except Exception as e:
        print(f"Error in advice endpoint: {e}")
        fallback = generate_fallback_advice(payload.task, payload.phase, payload.locale)
        return AdviceOut(**fallback)

@app.post("/search", response_model=List[DocumentOut])
def search_documents(payload: DocumentSearch):
    """RAG: Search knowledge base"""
    results = search_knowledge_base(payload.query, "all", payload.limit)
    return [DocumentOut(**doc) for doc in results]

@app.get("/health")
def health():
    return {
        "status": "ok", 
        "message": "Female Task Planner RAG API is running",
        "rag_enabled": True,
        "ai_available": model is not None
    }

@app.get("/")
def root():
    return {
        "message": "Female Task Planner RAG API", 
        "version": "2.0.0",
        "features": ["RAG", "AI-powered advice", "Knowledge retrieval"]
    }

@app.get("/phases")
def get_phases():
    """Get all cycle phases with detailed information"""
    return {"phases": RAG_KNOWLEDGE_BASE}

@app.get("/phases/{phase}")
def get_phase_details(phase: str):
    """Get detailed information about specific phase"""
    if phase not in RAG_KNOWLEDGE_BASE:
        raise HTTPException(status_code=404, detail="Phase not found")
    return {"phase": phase, "data": RAG_KNOWLEDGE_BASE[phase]}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Female Task Planner RAG API...")
    print("📚 RAG System: Knowledge base loaded")
    print("🤖 AI Status:", "Available" if model else "Fallback mode")
    uvicorn.run(app, host="127.0.0.1", port=8000)
