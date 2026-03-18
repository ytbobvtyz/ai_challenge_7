import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Challenge Day 3 - Honest Experiment"
    }
)

MODEL = "arcee-ai/trinity-large-preview:free" # nvidia/nemotron-3-nano-30b-a3b:free, stepfun/step-3.5-flash:free, arcee-ai/trinity-large-preview:free,
TASK = """Жили-были три брата: Мо, Ко и Ло. 
Мо был богат и знаменит.
Ло заведовал ломбардом, который посещал пьяница Ко.
Вопрос: при чём тут корова?"""

def save_response(approach_name, prompt, response, stats):
    filename = f"honest_{approach_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"ПОДХОД: {approach_name}\n")
        f.write("="*60 + "\n")
        f.write(f"ПРОМПТ (ТОЛЬКО ЭТО ПОЛУЧИЛА МОДЕЛЬ):\n{prompt}\n")
        f.write("-"*60 + "\n")
        f.write(f"ОТВЕТ:\n{response}\n")
    print(f"💾 Сохранено в {filename}")

def analyze_response(text, approach_name):
    if not text:
        return {}
    
    words = text.split()
    
    # Ключевые маркеры (для анализа, не для подсказки!)
    phonetic_hints = ['звук', 'произнес', 'быстро', 'вместе', 'слыш']
    milk_hints = ['молок', 'корова']
    
    return {
        'approach': approach_name,
        'length_words': len(words),
        'found_phonetic': any(h in text.lower() for h in phonetic_hints),
        'found_milk': any(h in text.lower() for h in milk_hints),
        'correct': ('молок' in text.lower() and 'корова' in text.lower()) or 
                   ('мо+ко+ло' in text.lower().replace(' ', ''))
    }

def run_honest_experiment():
    print("\n" + "="*100)
    print("🧪 ЧЕСТНЫЙ ЭКСПЕРИМЕНТ: Загадка про трёх братьев")
    print("="*100)
    print(f"Задача (ОДИНАКОВАЯ ДЛЯ ВСЕХ):\n{TASK}\n")
    print("⚠️  ВНИМАНИЕ: Никаких подсказок! Только чистое мышление модели.\n")
    
    results = []
    
    # 1. ПРЯМОЙ ОТВЕТ
    print("\n" + "📌"*30)
    print("📌 ПОДХОД 1: Прямой ответ")
    print("📌"*30)
    
    prompt1 = TASK
    response1 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt1}],
        temperature=0.3
    ).choices[0].message.content
    
    print(f"🤖 ОТВЕТ 1:\n{response1}\n")
    stats1 = analyze_response(response1, "Прямой ответ")
    save_response("Прямой ответ", prompt1, response1, stats1)
    results.append(('Прямой ответ', response1, stats1))
    
    # 2. ПОШАГОВОЕ РЕШЕНИЕ (без подсказок!)
    print("\n" + "📌"*30)
    print("📌 ПОДХОД 2: Пошаговое решение")
    print("📌"*30)
    
    prompt2 = TASK + "\n\nРешай задачу пошагово. Опиши каждый шаг своих рассуждений."
    # Никаких "произнеси быстро"! Только требование пошаговости.
    
    response2 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt2}],
        temperature=0.3
    ).choices[0].message.content
    
    print(f"🤖 ОТВЕТ 2:\n{response2}\n")
    stats2 = analyze_response(response2, "Пошаговое")
    save_response("Пошаговое", prompt2, response2, stats2)
    results.append(('Пошаговое', response2, stats2))
    
    # 3. МЕТА-ПРОМПТИНГ (без подсказок!)
    print("\n" + "📌"*30)
    print("📌 ПОДХОД 3: Мета-промптинг")
    print("📌"*30)
    
    meta_prompt = f"""Задача: {TASK}

Составь промпт для решения этой задачи. Промпт должен быть чётким и структурированным.
Напиши ТОЛЬКО промпт, без пояснений."""
    # Никаких "обрати внимание на звуки"! Просто составь промпт.
    
    generated_prompt = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": meta_prompt}],
        temperature=0.4
    ).choices[0].message.content
    
    print(f"🤖 СГЕНЕРИРОВАННЫЙ ПРОМПТ:\n{generated_prompt}\n")
    
    response3 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": generated_prompt}],
        temperature=0.3
    ).choices[0].message.content
    
    print(f"🤖 ОТВЕТ 3:\n{response3}\n")
    stats3 = analyze_response(response3, "Мета-промптинг")
    save_response("Мета-промптинг", generated_prompt, response3, stats3)
    results.append(('Мета-промптинг', response3, stats3))
    
    # 4. ГРУППА ЭКСПЕРТОВ (без специализации!)
    print("\n" + "📌"*30)
    print("📌 ПОДХОД 4: Группа экспертов")
    print("📌"*30)
    
    prompt4 = f"""Задача: {TASK}

Ты — группа из трёх экспертов. Каждый дай свой анализ задачи, а потом сформулируйте общий вывод.

Математик
Ветеринар
Инженер
Поэт-песенник

Оформи ответ так:
[ЭКСПЕРТ 1]
...
[ЭКСПЕРТ 2]
...
[ЭКСПЕРТ 3]
...
[ОБЩИЙ ВЫВОД]
..."""
    # Никаких имён! Просто эксперт 1,2,3. Пусть сами решают, кто они.
    
    response4 = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt4}],
        temperature=0.4
    ).choices[0].message.content
    
    print(f"🤖 ОТВЕТ 4:\n{response4}\n")
    stats4 = analyze_response(response4, "Группа экспертов")
    save_response("Группа экспертов", prompt4, response4, stats4)
    results.append(('Группа экспертов', response4, stats4))
    
    # ИТОГОВОЕ СРАВНЕНИЕ
    print("\n" + "="*100)
    print("📊 ИТОГОВОЕ СРАВНЕНИЕ (ЧЕСТНЫЙ ЭКСПЕРИМЕНТ)")
    print("="*100)
    
    print(f"""
    ┌─────────────────────┬─────────────────────────────────────────────────────┐
    │ Характеристика      │ Прямой    │ Пошагово  │ Мета      │ Эксперты   │
    ├─────────────────────┼───────────┼───────────┼───────────┼───────────┤
    │ Длина (слова)       │ {stats1['length_words']:<9} │ {stats2['length_words']:<9} │ {stats3['length_words']:<9} │ {stats4['length_words']:<9} │
    │ Заметила фонетику   │ {str(stats1['found_phonetic']):<9} │ {str(stats2['found_phonetic']):<9} │ {str(stats3['found_phonetic']):<9} │ {str(stats4['found_phonetic']):<9} │
    │ Связала с молоком   │ {str(stats1['found_milk']):<9} │ {str(stats2['found_milk']):<9} │ {str(stats3['found_milk']):<9} │ {str(stats4['found_milk']):<9} │
    │ ПРАВИЛЬНЫЙ ОТВЕТ    │ {str(stats1['correct']):<9} │ {str(stats2['correct']):<9} │ {str(stats3['correct']):<9} │ {str(stats4['correct']):<9} │
    └─────────────────────┴───────────┴───────────┴───────────┴───────────┘
    """)
    
    # Сохраняем результаты
    summary = {
        'task': TASK,
        'model': MODEL,
        'date': datetime.now().isoformat(),
        'disclaimer': 'Честный эксперимент без подсказок',
        'results': [
            {
                'approach': r[0],
                'stats': r[2]
            } for r in results
        ]
    }
    
    with open('honest_cow_riddle.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n📄 Честный отчёт сохранён в honest_cow_riddle.json")

if __name__ == "__main__":
    run_honest_experiment()