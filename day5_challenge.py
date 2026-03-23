# day5_challenge_gemma.py

import os
import time
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Challenge Day 5 - Gemma Musical Mathematics"
    }
)

# ============================================================
# ТРИ МОДЕЛИ 
# ============================================================
MODELS = {
    "weak": {
        "id": "arcee-ai/trinity-mini:free",
        "name": "trinity-mini",
        "tier": "Слабая (4B params, стабильная)",
        "context": "32K",
        "strength": "Легкая для простых инструкций"
    },
    "medium": {
        "id": "stepfun/step-3.5-flash:free",
        "name": "Step 3.5 Flash",
        "tier": "Средняя (196B total / 11B active)",
        "context": "256K",
        "strength": "баланс скорости и глубины"
    },
    "strong": {
        "id": "nvidia/nemotron-3-super-120b-a12b:free",
        "name": "NVIDIA Nemotron 3 Super 120B",
        "tier": "Сильная (120B total / 12B active)",
        "context": "256K",
        "strength": "максимальная глубина"
    }
}

# ============================================================
# ПРОМПТ (музыкально-математический)
# ============================================================
TASK = """Если бы музыка была математикой, какие основные 5 положений ты бы выделил? Опиши их математическим языком с текстовым пояснением."""

DELAY_SECONDS = 3

def safe_filename(text):
    """Преобразует название модели в безопасное имя файла"""
    return text.replace(' ', '_').replace('/', '_').lower()

def test_model_directly(model_id):
    """Проверяет доступность модели"""
    try:
        print(f"   Проверяю {model_id}...", end=" ")
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "Привет, ответь 'OK'"}],
            max_tokens=5,
            temperature=0
        )
        print("✅ доступна")
        return True
    except Exception as e:
        print(f"❌ недоступна: {str(e)[:80]}")
        return False

def save_answer_to_file(model_name, model_id, answer, stats, timestamp):
    """Сохраняет полный ответ модели в отдельный файл"""
    filename = f"day5_{safe_filename(model_name)}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write(f"ЭКСПЕРИМЕНТ: Музыка как математика\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"МОДЕЛЬ: {model_name}\n")
        f.write(f"ID: {model_id}\n")
        f.write(f"Уровень: {stats['tier']}\n")
        f.write(f"Контекст: {stats['context']}\n")
        f.write(f"Сильная сторона: {stats['strength']}\n\n")
        
        f.write("="*70 + "\n")
        f.write("ПРОМПТ:\n")
        f.write("="*70 + "\n")
        f.write(TASK + "\n\n")
        
        f.write("="*70 + "\n")
        f.write("ОТВЕТ МОДЕЛИ:\n")
        f.write("="*70 + "\n")
        f.write(answer + "\n\n")
        
        f.write("="*70 + "\n")
        f.write("СТАТИСТИКА:\n")
        f.write("="*70 + "\n")
        f.write(f"⏱️ Время ответа: {stats['time_seconds']} сек\n")
        f.write(f"📝 Токенов (всего): {stats['total_tokens']}\n")
        f.write(f"   - prompt_tokens: {stats['prompt_tokens']}\n")
        f.write(f"   - completion_tokens: {stats['completion_tokens']}\n")
        f.write(f"📏 Длина ответа: {stats['answer_length']} символов\n")
        f.write(f"📊 Количество слов: {stats['word_count']}\n")
    
    print(f"💾 Сохранено: {filename}")
    return filename

def run_model_test(model_key):
    """Тестирует одну модель"""
    model = MODELS[model_key]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"\n{'='*65}")
    print(f"🎵 Тестируем: {model['name']}")
    print(f"📊 Уровень: {model['tier']}")
    print(f"📏 Контекст: {model['context']}")
    print(f"💪 Сильная сторона: {model['strength']}")
    print('='*65)
    
    # Проверяем доступность
    if not test_model_directly(model["id"]):
        return None
    
    try:
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model=model["id"],
            messages=[{"role": "user", "content": TASK}],
            temperature=0.7,
            max_tokens=1500
        )
        
        elapsed_time = time.time() - start_time
        answer = completion.choices[0].message.content
        usage = completion.usage
        
        stats = {
            'model_name': model['name'],
            'model_id': model['id'],
            'tier': model['tier'],
            'context': model['context'],
            'strength': model['strength'],
            'time_seconds': round(elapsed_time, 2),
            'prompt_tokens': usage.prompt_tokens,
            'completion_tokens': usage.completion_tokens,
            'total_tokens': usage.total_tokens,
            'answer_length': len(answer),
            'word_count': len(answer.split()),
            'answer': answer,
            'timestamp': timestamp
        }
        
        # Показываем превью
        preview = answer[:400] + "..." if len(answer) > 400 else answer
        print(f"\n🎼 МЕМОРАНДУМ (первые строки):\n{preview}\n")
        
        print(f"📊 СТАТИСТИКА:")
        print(f"  ⏱️ Время: {stats['time_seconds']} сек")
        print(f"  📝 Токенов: {stats['total_tokens']} (in: {stats['prompt_tokens']}, out: {stats['completion_tokens']})")
        print(f"  📏 Длина: {stats['answer_length']} символов, {stats['word_count']} слов")
        
        # Сохраняем в файл
        filename = save_answer_to_file(model['name'], model['id'], answer, stats, timestamp)
        stats['filename'] = filename
        
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def analyze_answer(text):
    """Анализирует ответ по ключевым метрикам"""
    if not text:
        return {}
    
    text_lower = text.lower()
    
    # Структура документа
    has_axioms = any(w in text_lower for w in ['аксиом', 'закон', 'постулат', 'фундаментальн'])
    has_theorems = any(w in text_lower for w in ['теорем', 'следстви', 'вытека', 'доказательств'])
    has_applications = any(w in text_lower for w in ['применени', 'вычислени', 'практическ'])
    
    structure_score = sum([has_axioms, has_theorems, has_applications])
    
    # Математическая глубина
    math_markers = [
        'функци', 'множеств', 'отношени', 'структур', 'пространств',
        'оператор', 'преобразовани', 'изоморфизм', 'алгебра', 'вектор',
        'числ', 'пропорци', 'аксиоматик', 'модель'
    ]
    math_depth = sum(1 for m in math_markers if m in text_lower)
    
    # Музыкальная глубина
    music_markers = [
        'гармони', 'ритм', 'мелоди', 'аккорд', 'интервал', 'октав',
        'тон', 'полутон', 'нот', 'лад', 'тональност', 'тембр', 'пауз',
        'длительност', 'темп', 'консонанс', 'диссонанс', 'звукоряд'
    ]
    music_depth = sum(1 for m in music_markers if m in text_lower)
    
    # Креативность (неожиданные связи)
    creative_markers = [
        'фрактал', 'фибоначчи', 'симметри', 'золотое сечени', 'квант',
        'волн', 'частот', 'резонанс', 'энтропи', 'информаци', 'хаос'
    ]
    creativity = sum(1 for m in creative_markers if m in text_lower)
    
    return {
        'structure_score': structure_score,
        'has_axioms': has_axioms,
        'has_theorems': has_theorems,
        'has_applications': has_applications,
        'math_depth': math_depth,
        'music_depth': music_depth,
        'creativity': creativity,
        'total_score': structure_score + math_depth/5 + music_depth/5 + creativity/3,
        'length': len(text)
    }

def create_comparison_table(results, analyses):
    """Создает и сохраняет таблицу сравнения"""
    print("\n" + "="*70)
    print("🏆 ИТОГОВОЕ СРАВНЕНИЕ МОДЕЛЕЙ GOOGLE GEMMA")
    print("="*70)
    
    print(f"""
┌─────────────────────────────┬─────────────────┬─────────────────┬─────────────────┐
│         Критерий            │   
│                             │    (слабая)     │   (средняя)     │   (сильная)     │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ ⏱️ Время ответа (сек)       │ {results[0]['time_seconds']:<15} │ {results[1]['time_seconds']:<15} │ {results[2]['time_seconds']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 📝 Всего токенов            │ {results[0]['total_tokens']:<15} │ {results[1]['total_tokens']:<15} │ {results[2]['total_tokens']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 📏 Длина ответа (симв)      │ {results[0]['answer_length']:<15} │ {results[1]['answer_length']:<15} │ {results[2]['answer_length']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 📐 Математическая глубина   │ {analyses[0]['math_depth']:<15} │ {analyses[1]['math_depth']:<15} │ {analyses[2]['math_depth']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 🎵 Музыкальная глубина      │ {analyses[0]['music_depth']:<15} │ {analyses[1]['music_depth']:<15} │ {analyses[2]['music_depth']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 💡 Креативность             │ {analyses[0]['creativity']:<15} │ {analyses[1]['creativity']:<15} │ {analyses[2]['creativity']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 🏛️ Структура (0-3)          │ {analyses[0]['structure_score']:<15} │ {analyses[1]['structure_score']:<15} │ {analyses[2]['structure_score']:<15} │
├─────────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 🏆 ИТОГОВЫЙ БАЛЛ            │ {analyses[0]['total_score']:<15.1f} │ {analyses[1]['total_score']:<15.1f} │ {analyses[2]['total_score']:<15.1f} │
└─────────────────────────────┴─────────────────┴─────────────────┴─────────────────┘
""")
    
    # Определяем победителей
    metrics = [
        ('Математическая глубина', 'math_depth'),
        ('Музыкальная глубина', 'music_depth'),
        ('Креативность', 'creativity'),
        ('Общий балл', 'total_score')
    ]
    
    print("\n🏆 ПОБЕДИТЕЛИ В НОМИНАЦИЯХ:")
    for metric_name, metric_key in metrics:
        best_idx = max(range(len(analyses)), key=lambda i: analyses[i][metric_key])
        model_names = ["Слабая", "Средняя", "Сильная"]
        print(f"   {metric_name}: {model_names[best_idx]}")
    
    print("\n📋 КЛЮЧЕВЫЕ ВЫВОДЫ:")
    print("   • Слабая: самая быстрая, но поверхностная. Для быстрых прототипов.")
    print("   • Средняя: золотая середина, баланс скорости и глубины.")
    print("   • Сильная: самая глубокая, но медленнее. Для сложных аналитических задач.")
    
    print("\n💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
    print("   • Для чат-ботов и простых задач: Слабая")
    print("   • Для reasoning и аналитики: Средняя")
    print("   • Для сложных агентных систем: Сильная")

def save_comparison_json(results, analyses):
    """Сохраняет JSON-отчет для дальнейшего анализа"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'task': TASK,
        'models': []
    }
    
    for i, (res, ana) in enumerate(zip(results, analyses)):
        report['models'].append({
            'name': res['model_name'],
            'id': res['model_id'],
            'tier': res['tier'],
            'performance': {
                'time_seconds': res['time_seconds'],
                'prompt_tokens': res['prompt_tokens'],
                'completion_tokens': res['completion_tokens'],
                'total_tokens': res['total_tokens'],
                'answer_length': res['answer_length'],
                'word_count': res['word_count']
            },
            'analysis': ana,
            'saved_file': res['filename']
        })
    
    filename = f"day5_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Полный JSON-отчет сохранен в {filename}")
    return filename

if __name__ == "__main__":
    print("\n" + "🎵"*40)
    print("🎵 ДЕНЬ 5: МУЗЫКА КАК МАТЕМАТИКА")
    print("🎵 Сравнение Google Gemma: 4B | 12B | 27B")
    print("🎵"*40)
    
    print(f"\n📜 ЗАДАНИЕ ДЛЯ МОДЕЛЕЙ:")
    print("   Создать Меморандум Математической Музыки")
    print("   Оценивается: математическая строгость, музыкальная глубина, креативность\n")
    
    results = []
    
    for i, key in enumerate(['weak', 'medium', 'strong']):
        if i > 0:
            print(f"\n⏳ Пауза {DELAY_SECONDS} секунд...")
            time.sleep(DELAY_SECONDS)
        
        result = run_model_test(key)
        if result:
            results.append(result)
    
    if len(results) == 3:
        analyses = [analyze_answer(r['answer']) for r in results]
        create_comparison_table(results, analyses)
        save_comparison_json(results, analyses)
        
        print("\n" + "="*70)
        print("✅ ЭКСПЕРИМЕНТ ЗАВЕРШЕН!")
        print("="*70)
        print("\n📁 СОХРАНЕННЫЕ ФАЙЛЫ:")
        for r in results:
            print(f"   • {r['filename']}")
        print(f"\n💡 Теперь можешь вручную сравнить ответы моделей в сохраненных файлах.")
        print("   Обрати внимание на:")
        print("   - Как меняется глубина математических рассуждений с ростом модели")
        print("   - Появляются ли новые музыкальные образы у 27B")
        print("   - Насколько структурирован меморандум в каждой версии")
    else:
        print(f"\n⚠️ Получено {len(results)} из 3 ответов.")
        print("   Попробуй запустить ещё раз или проверь доступность моделей.")