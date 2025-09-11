#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

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

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found! Please check your .env file")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Pydantic models
class AdviceIn(BaseModel):
    task: str
    phase: str
    locale: str = "ru"

class AdviceOut(BaseModel):
    verdict: str  # "good", "ok", "avoid"
    reason: str
    suggestion: str

# Knowledge base about menstrual cycle phases
KNOWLEDGE_BASE = {
    "menstruation": {
        "description": "Менструация (1-5 день цикла)",
        "characteristics": "низкая энергия, усталость, возможны спазмы",
        "recommendations": "отдых, легкие задачи, избегание стресса"
    },
    "follicular": {
        "description": "Фолликулярная фаза (6-10 день цикла)",
        "characteristics": "повышение энергии, хорошее настроение, мотивация",
        "recommendations": "планирование, обучение, новые проекты"
    },
    "ovulation": {
        "description": "Овуляция (11-15 день цикла)",
        "characteristics": "пик энергии, высокая коммуникабельность, уверенность",
        "recommendations": "встречи, презентации, важные переговоры"
    },
    "luteal": {
        "description": "Лютеальная фаза (16-28 день цикла)",
        "characteristics": "снижение энергии, возможны перепады настроения",
        "recommendations": "завершение проектов, детальная работа, делегирование"
    }
}

def get_phase_info(phase: str) -> dict:
    """Get information about menstrual cycle phase"""
    return KNOWLEDGE_BASE.get(phase, {
        "description": "Неизвестная фаза",
        "characteristics": "недостаточно данных",
        "recommendations": "ориентируйтесь на самочувствие"
    })

def generate_advice(task: str, phase: str, locale: str) -> dict:
    """Generate AI advice for task based on cycle phase"""
    phase_info = get_phase_info(phase)
    
    if locale == "ru":
        prompt = f"""Ты - эксперт по женскому здоровью и менструальному циклу.

Фаза цикла: {phase_info['description']}
Характеристики фазы: {phase_info['characteristics']}
Общие рекомендации: {phase_info['recommendations']}

Задача: {task}

Проанализируй эту задачу с учетом фазы менструального цикла и дай персональный совет.

Отвечай в формате JSON с полями:
- verdict: "good" (отлично), "ok" (нормально), "avoid" (избегать)
- reason: объяснение почему
- suggestion: конкретный совет

Пример ответа:
{{"verdict": "good", "reason": "пик энергии", "suggestion": "отличное время для важных встреч"}}"""
    else:
        prompt = f"""You are an expert in women's health and menstrual cycle.

Cycle phase: {phase_info['description']}
Phase characteristics: {phase_info['characteristics']}
General recommendations: {phase_info['recommendations']}

Task: {task}

Analyze this task considering the menstrual cycle phase and give personalized advice.

Respond in JSON format with fields:
- verdict: "good", "ok", "avoid"
- reason: explanation why
- suggestion: specific advice

Example response:
{{"verdict": "good", "reason": "peak energy", "suggestion": "great time for important meetings"}}"""

    try:
        response = model.generate_content(prompt)
        # Try to parse JSON from response
        text = response.text.strip()
        
        # Extract JSON from response if it's wrapped in markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # Parse JSON
        try:
            result = json.loads(text)
            return {
                "verdict": result.get("verdict", "ok"),
                "reason": result.get("reason", ""),
                "suggestion": result.get("suggestion", "")
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return get_fallback_advice(phase, locale)
            
    except Exception as e:
        print(f"Error generating advice: {e}")
        return get_fallback_advice(phase, locale)

def get_fallback_advice(phase: str, locale: str) -> dict:
    """Fallback advice when AI is not available"""
    fallback = {
        "menstruation": {
            "ru": ("avoid", "низкая энергия", "перенеси или упрости задачу"),
            "en": ("avoid", "low energy", "postpone or simplify the task")
        },
        "follicular": {
            "ru": ("good", "хорошее время для старта", "запланируй первые шаги"),
            "en": ("good", "good time to start", "plan the first steps")
        },
        "ovulation": {
            "ru": ("good", "пик коммуникаций", "назначь встречи/презентации"),
            "en": ("good", "peak communication", "schedule meetings/presentations")
        },
        "luteal": {
            "ru": ("ok", "фокус и завершение", "разбей на подзадачи"),
            "en": ("ok", "focus and completion", "break into subtasks")
        }
    }
    
    phase_data = fallback.get(phase, fallback["follicular"])
    lang_data = phase_data.get(locale, phase_data["ru"])
    
    return {
        "verdict": lang_data[0],
        "reason": lang_data[1],
        "suggestion": lang_data[2]
    }

# API endpoints
@app.post("/advice", response_model=AdviceOut)
def advice(payload: AdviceIn):
    try:
        # Generate AI advice
        advice_data = generate_advice(payload.task, payload.phase, payload.locale)
        
        # Validate verdict
        if advice_data["verdict"] not in ("good", "ok", "avoid"):
            advice_data["verdict"] = "ok"
            
        return AdviceOut(**advice_data)
        
    except Exception as e:
        print(f"Error in advice endpoint: {e}")
        # Return fallback response
        fallback = get_fallback_advice(payload.phase, payload.locale)
        return AdviceOut(**fallback)

@app.get("/health")
def health():
    return {"status": "ok", "message": "Female Task Planner API is running"}

@app.get("/")
def root():
    return {"message": "Female Task Planner API", "version": "1.0.0"}

@app.get("/phases")
def get_phases():
    """Get information about all cycle phases"""
    return {"phases": KNOWLEDGE_BASE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
