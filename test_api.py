#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"

def test_health():
    """Тест health endpoint"""
    print("🔍 Тестируем health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check прошел успешно")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_advice():
    """Тест advice endpoint"""
    print("\n🔍 Тестируем advice endpoint...")
    
    test_cases = [
        {
            "task": "Провести презентацию",
            "phase": "ovulation",
            "locale": "ru",
            "expected_verdict": "good"
        },
        {
            "task": "Сложная аналитическая работа",
            "phase": "menstruation",
            "locale": "ru",
            "expected_verdict": "avoid"
        },
        {
            "task": "Планирование проекта",
            "phase": "follicular",
            "locale": "ru",
            "expected_verdict": "good"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   Тест {i}: {test_case['task']} ({test_case['phase']})")
        try:
            response = requests.post(
                f"{API_BASE}/advice",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Ответ получен: {data}")
                
                # Проверяем структуру ответа
                required_fields = ["verdict", "reason", "suggestion"]
                if all(field in data for field in required_fields):
                    print(f"   ✅ Структура ответа корректна")
                    success_count += 1
                else:
                    print(f"   ❌ Отсутствуют обязательные поля")
            else:
                print(f"   ❌ Ошибка API: {response.status_code}")
                print(f"   Ответ: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Ошибка запроса: {e}")
    
    print(f"\n📊 Результат: {success_count}/{len(test_cases)} тестов прошли успешно")
    return success_count == len(test_cases)

def test_root():
    """Тест root endpoint"""
    print("\n🔍 Тестируем root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint работает")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def main():
    print("🧪 Запуск тестов Female Task Planner API")
    print("=" * 50)
    
    # Ждем немного для запуска сервера
    print("⏳ Ждем запуска сервера...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Advice Endpoint", test_advice)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"❌ Тест {test_name} не прошел")
    
    print(f"\n{'='*50}")
    print(f"📊 Итого: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        return True
    else:
        print("⚠️  Некоторые тесты не прошли. Проверьте настройки.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
