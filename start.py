#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_env_file():
    """Проверяем наличие .env файла"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("📝 Создайте файл .env с вашим Google API ключом:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False
    return True

def check_dependencies():
    """Проверяем установлены ли зависимости"""
    try:
        import fastapi
        import uvicorn
        import langchain
        print("✅ Зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Не установлены зависимости: {e}")
        print("📦 Установите зависимости: pip install -r api/requirements.txt")
        return False

def start_backend():
    """Запускаем backend сервер"""
    print("🚀 Запускаем backend сервер...")
    os.chdir("api")
    try:
        subprocess.Popen([sys.executable, "main_simple.py"])
        print("✅ Backend запущен на http://127.0.0.1:8000")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска backend: {e}")
        return False

def open_frontend():
    """Открываем frontend в браузере"""
    print("🌐 Открываем frontend...")
    frontend_path = Path("../Frontend/index.html").resolve()
    webbrowser.open(f"file://{frontend_path}")
    print("✅ Frontend открыт в браузере")

def main():
    print("🌸 Female Task Planner - Запуск системы")
    print("=" * 50)
    
    # Проверяем .env файл
    if not check_env_file():
        return
    
    # Проверяем зависимости
    if not check_dependencies():
        return
    
    # Запускаем backend
    if not start_backend():
        return
    
    # Ждем немного для запуска сервера
    print("⏳ Ждем запуска сервера...")
    time.sleep(3)
    
    # Открываем frontend
    open_frontend()
    
    print("\n🎉 Система запущена!")
    print("📱 Frontend: откройте Frontend/index.html в браузере")
    print("🔧 Backend API: http://127.0.0.1:8000")
    print("📖 Документация API: http://127.0.0.1:8000/docs")
    print("\n💡 Для остановки нажмите Ctrl+C")

if __name__ == "__main__":
    try:
        main()
        # Держим скрипт запущенным
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Остановка системы...")
        sys.exit(0)
