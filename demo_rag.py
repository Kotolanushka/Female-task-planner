#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Демонстрационный скрипт для Female Task Planner RAG системы
Показывает возможности RAG (Retrieval-Augmented Generation) для анализа задач
"""

import requests
import json
import time
from typing import List, Dict

API_BASE = "http://127.0.0.1:8000"

def print_header(title: str):
    """Красивый заголовок"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Заголовок секции"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_rag_retrieval():
    """Демонстрация RAG retrieval"""
    print_section("RAG Retrieval - Поиск в базе знаний")
    
    queries = [
        "энергия и продуктивность",
        "важные встречи и презентации", 
        "творческие задачи",
        "завершение проектов"
    ]
    
    for query in queries:
        try:
            response = requests.post(f"{API_BASE}/search", json={"query": query, "limit": 2})
            if response.status_code == 200:
                results = response.json()
                print(f"\n🔍 Запрос: '{query}'")
                for i, doc in enumerate(results, 1):
                    print(f"   {i}. {doc['content']} (релевантность: {doc['relevance_score']:.2f})")
            else:
                print(f"❌ Ошибка поиска: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def demo_phase_analysis():
    """Демонстрация анализа фаз цикла"""
    print_section("Анализ фаз менструального цикла")
    
    phases = ["menstruation", "follicular", "ovulation", "luteal"]
    
    for phase in phases:
        try:
            response = requests.get(f"{API_BASE}/phases/{phase}")
            if response.status_code == 200:
                data = response.json()["data"]
                print(f"\n🔴 {phase.upper()}")
                print(f"   Дни: {data['phase_info']['days']}")
                print(f"   Физические эффекты: {', '.join(data['physical_effects'][:3])}...")
                print(f"   Когнитивные эффекты: {', '.join(data['cognitive_effects'][:3])}...")
        except Exception as e:
            print(f"❌ Ошибка получения фазы {phase}: {e}")

def demo_ai_advice():
    """Демонстрация AI-советов с RAG"""
    print_section("AI-советы с RAG контекстом")
    
    test_cases = [
        {
            "task": "Провести важную презентацию для клиентов",
            "phase": "ovulation",
            "expected": "good"
        },
        {
            "task": "Сложная аналитическая работа с данными",
            "phase": "menstruation", 
            "expected": "avoid"
        },
        {
            "task": "Планирование нового проекта",
            "phase": "follicular",
            "expected": "good"
        },
        {
            "task": "Завершение отчета и подготовка к сдаче",
            "phase": "luteal",
            "expected": "good"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            response = requests.post(f"{API_BASE}/advice", json=case)
            if response.status_code == 200:
                advice = response.json()
                print(f"\n📝 Тест {i}: {case['task']}")
                print(f"   Фаза: {case['phase']}")
                print(f"   Вердикт: {advice['verdict']} (ожидался: {case['expected']})")
                print(f"   Причина: {advice['reason']}")
                print(f"   Совет: {advice['suggestion']}")
                print(f"   Уверенность: {advice['confidence']:.2f}")
                print(f"   Источник: {advice['source']}")
            else:
                print(f"❌ Ошибка API: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def demo_rag_architecture():
    """Демонстрация архитектуры RAG"""
    print_section("Архитектура RAG системы")
    
    print("""
🏗️  RAG (Retrieval-Augmented Generation) архитектура:

1. 📚 KNOWLEDGE BASE (База знаний)
   - Структурированные данные о фазах цикла
   - Физические и когнитивные эффекты
   - Рекомендации по продуктивности
   - Специфичные советы по задачам

2. 🔍 RETRIEVAL (Извлечение)
   - Поиск релевантной информации по запросу
   - Ключевое слово сопоставление
   - Ранжирование по релевантности
   - Контекстная фильтрация

3. 🤖 GENERATION (Генерация)
   - AI-модель (Google Gemini) для генерации советов
   - Fallback система при недоступности AI
   - Контекстно-зависимые рекомендации
   - Персонализированные советы

4. 📊 EVALUATION (Оценка)
   - Confidence scoring
   - Source attribution
   - Quality metrics
   - Fallback detection
    """)

def demo_api_endpoints():
    """Демонстрация API endpoints"""
    print_section("API Endpoints")
    
    endpoints = [
        ("GET", "/health", "Проверка состояния системы"),
        ("GET", "/phases", "Получить все фазы цикла"),
        ("GET", "/phases/{phase}", "Детали конкретной фазы"),
        ("POST", "/search", "Поиск в базе знаний (RAG)"),
        ("POST", "/advice", "Получить AI-совет с RAG контекстом")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"   {method:4} {endpoint:20} - {description}")

def check_api_status():
    """Проверка статуса API"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Status: Online")
            print(f"   RAG Enabled: {data.get('rag_enabled', False)}")
            print(f"   AI Available: {data.get('ai_available', False)}")
            return True
        else:
            print(f"❌ API Status: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Status: Offline - {e}")
        return False

def main():
    """Главная функция демонстрации"""
    print_header("Female Task Planner RAG System Demo")
    print("🎯 Демонстрация навыков создания RAG систем")
    print("📚 Retrieval-Augmented Generation для анализа задач")
    
    # Проверяем API
    if not check_api_status():
        print("\n❌ API недоступен. Запустите сервер:")
        print("   cd api && python3 main_rag.py")
        return
    
    # Демонстрации
    demo_rag_architecture()
    demo_api_endpoints()
    demo_phase_analysis()
    demo_rag_retrieval()
    demo_ai_advice()
    
    print_header("Демонстрация завершена")
    print("🎉 RAG система успешно продемонстрирована!")
    print("\n💡 Ключевые особенности:")
    print("   • Структурированная база знаний")
    print("   • Интеллектуальный поиск и извлечение")
    print("   • AI-генерация с контекстом")
    print("   • Fallback система для надежности")
    print("   • RESTful API для интеграции")

if __name__ == "__main__":
    main()
