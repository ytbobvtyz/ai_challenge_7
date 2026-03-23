import os
import time
import json
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Challenge Day 5 - Musical Mathematics"
    }
)


def get_available_models():
    """Получает актуальный список моделей из API"""
    print("\n🔍 Проверяю доступные модели...")
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"
        }
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            models_data = response.json()
            free_models = [m['id'] for m in models_data['data'] if ':free' in m['id']]
            print (free_models)
            print(f"✅ Доступно {len(free_models)} бесплатных моделей")
            return free_models
    except Exception as e:
        print(f"⚠️ Не удалось получить список моделей: {e}")
    return None

get_available_models()