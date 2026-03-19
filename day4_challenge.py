# day4_temperature_experiment_napoleon.py

import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Загружаем ключ
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Challenge Day 4 - Napoleon"
    }
)

# Константы
MODEL = "stepfun/step-3.5-flash:free"  # Твоя любимая модель
TEMPERATURES = [0, 0.7, 1.2]
DELAY_SECONDS = 5

# Промпт про Наполеона (твой, с небольшим уточнением)
TASK = """Научи меня как стать единственным человеком и руководителем корпорации из ИИ-агентов в пять действий, будь изобретательным и точным. Каждое действие - описанов в 2-3 предложениях."""

def print_prompt():
    print("\n" + "📜"*35)
    print("📜 ИСПОЛЬЗУЕМЫЙ ПРОМПТ")
    print("📜"*35)
    print(TASK)
    print("\n" + "🚀"*35)
    print("🚀 ЭКСПЕРИМЕНТ: НАПОЛЕОН ПРИ T=0, 0.7, 1.2")
    print("🚀"*35)

def run_experiment(temp):
    print(f"\n{'='*60}")
    print(f"🌡️ TEMPERATURE = {temp}")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print('='*60)
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": TASK}],
            temperature=temp,
            max_tokens=1200
        )
        
        answer = completion.choices[0].message.content
        
        filename = f"napoleon_temp_{str(temp).replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"🌡️ TEMPERATURE = {temp}\n")
            f.write("="*60 + "\n")
            f.write(f"ПРОМПТ:\n{TASK}\n")
            f.write("-"*60 + "\n")
            f.write(f"ОТВЕТ:\n{answer}\n")
        
        print(f"\n{answer}\n")
        print(f"✅ Длина: {len(answer)} символов")
        print(f"💾 Сохранено: {filename}")
        
        return {
            'temp': temp,
            'answer': answer,
            'length': len(answer),
            'events': answer.count('\n') if answer else 0
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def analyze_answer(result):
    """Анализирует ответ по критериям"""
    if not result:
        return None
    
    text = result['answer']
    temp = result['temp']
    
    # Точность (наличие дат и мест)
    has_dates = any(c.isdigit() for c in text)  # есть ли цифры (даты)
    has_places = any(place in text.lower() for place in 
                     ['париж', 'тулон', 'итал', 'египет', 'франц'])
    
    # Креативность (эмоциональные маркеры)
    creativity_markers = ['блестящий', 'гениальный', 'судьбоносный', 
                          'легендарный', 'триумф', 'роковой']
    creativity_score = sum(1 for m in creativity_markers if m.lower() in text.lower())
    
    return {
        'temp': temp,
        'has_dates': has_dates,
        'has_places': has_places,
        'creativity_score': creativity_score,
        'events_count': result['events'],
        'length': result['length']
    }

if __name__ == "__main__":
    print_prompt()
    
    results = []
    
    for i, temp in enumerate(TEMPERATURES):
        if i > 0:
            print(f"\n⏳ Пауза {DELAY_SECONDS} секунд...")
            time.sleep(DELAY_SECONDS)
        
        result = run_experiment(temp)
        if result:
            results.append(result)
    
    # Анализ
    print("\n" + "="*70)
    print("📊 СРАВНЕНИЕ ОТВЕТОВ")
    print("="*70)
    
    analyses = [analyze_answer(r) for r in results if r]
    
    if len(analyses) == 3:
        print(f"""
    ┌─────────────────────┬────────────────────────────────────┐
    │ Критерий            │ T=0       │ T=0.7     │ T=1.2     │
    ├─────────────────────┼───────────┼───────────┼───────────┤
    │ Есть даты           │ {analyses[0]['has_dates']!s:<9} │ {analyses[1]['has_dates']!s:<9} │ {analyses[2]['has_dates']!s:<9} │
    │ Есть места          │ {analyses[0]['has_places']!s:<9} │ {analyses[1]['has_places']!s:<9} │ {analyses[2]['has_places']!s:<9} │
    │ Креативность        │ {analyses[0]['creativity_score']:<9} │ {analyses[1]['creativity_score']:<9} │ {analyses[2]['creativity_score']:<9} │
    │ Кол-во событий      │ {analyses[0]['events_count']:<9} │ {analyses[1]['events_count']:<9} │ {analyses[2]['events_count']:<9} │
    │ Длина ответа        │ {analyses[0]['length']:<9} │ {analyses[1]['length']:<9} │ {analyses[2]['length']:<9} │
    └─────────────────────┴───────────┴───────────┴───────────┘
    """)
    