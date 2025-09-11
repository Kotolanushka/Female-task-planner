# Настройка Female Task Planner

## 1. Создайте файл .env в корне проекта

Создайте файл `.env` со следующим содержимым:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# FastAPI Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=True
```

## 2. Получите Google Gemini API ключ

1. Перейдите на https://makersuite.google.com/app/apikey
2. Создайте новый API ключ
3. Скопируйте ключ в файл .env

## 3. Установите зависимости

```bash
cd api
pip install -r requirements.txt
```

## 4. Запустите backend

```bash
cd api
python main.py
```

## 5. Откройте frontend

Откройте файл `Frontend/index.html` в браузере.

## Структура проекта

- `api/` - Backend API на FastAPI
- `Frontend/` - Frontend на HTML/CSS/JS
- `Data/Knowledge/` - База знаний для AI
- `Backend/` - Демо RAG система
