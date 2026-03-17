import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Challenge - Model Self-Analysis"
    }
)

def analyze_response(text, role_name):
    """Анализирует ответ по разным метрикам"""
    if not text:
        return {}
    
    # Базовые метрики
    words = text.split()
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s for s in sentences if len(s.strip()) > 0]
    
    # Технические термины (для оценки варианта 3)
    tech_terms = ['attention', 'transformer', 'token', 'layer', 'neural', 'parameter', 
                  'gradient', 'inference', 'fine-tuning', 'embedding', 'architecture',
                  'алгоритм', 'нейросеть', 'слой', 'токен', 'архитектура']
    
    # Детские маркеры (для оценки варианта 2)
    child_markers = ['солнышк', 'зайчик', 'игрушк', 'кубик', 'мишк', 'сказк', 
                     'мультик', 'радуг', 'добрый', 'ласковый']
    
    # Английские слова (как маркер плохой адаптации)
    english_words = ['the', 'is', 'are', 'model', 'context', 'prompt', 'response', 
                     'temperature', 'token', 'layer', 'network', 'attention']
    
    tech_count = sum(1 for term in tech_terms if term.lower() in text.lower())
    child_count = sum(1 for marker in child_markers if marker.lower() in text.lower())
    english_count = sum(1 for word in english_words if f' {word} ' in f' {text.lower()} ')
    
    return {
        'role': role_name,
        'length_chars': len(text),
        'length_words': len(words),
        'avg_sentence_words': len(words) / len(sentences) if sentences else 0,
        'tech_terms': tech_count,
        'child_markers': child_count,
        'english_loans': english_count,
        'exclamations': text.count('!'),
        'questions': text.count('?'),
        'text_sample': text[:200] + '...' if len(text) > 200 else text
    }

def run_experiment(question, system_prompt, temperature, role_name):
    """Запускает один вариант эксперимента"""
    print(f"\n{'='*60}")
    print(f"🧪 ВАРИАНТ: {role_name}")
    print(f"Пользовательский промпт: {question}")
    print(f"🌡️ Температура: {temperature}")
    print(f"📋 Системный промпт: {system_prompt[:100]}..." if len(system_prompt) > 100 else f"📋 Системный промпт: {system_prompt}")
    print('='*60)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": question})
    
    try:
        completion = client.chat.completions.create(
            model="stepfun/step-3.5-flash:free",
            messages=messages,
            temperature=temperature,
            max_tokens=1000
        )
        answer = completion.choices[0].message.content
        print(f"\n🤖 ОТВЕТ:\n{answer}\n")
        
        # Анализ
        stats = analyze_response(answer, role_name)
        print(f"📊 АНАЛИЗ:")
        print(f"  - Длина: {stats['length_words']} слов, {stats['length_chars']} символов")
        print(f"  - Среднее предложение: {stats['avg_sentence_words']:.1f} слов")
        print(f"  - Технических терминов: {stats['tech_terms']}")
        print(f"  - Детских маркеров: {stats['child_markers']}")
        print(f"  - Английских вкраплений: {stats['english_loans']}")
        print(f"  - Восклицаний: {stats['exclamations']}, вопросов: {stats['questions']}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    print("="*70)
    print("🔬 ЭКСПЕРИМЕНТ: Модель объясняет саму себя в трех ролях")
    print("="*70)
    
    question = "Языковая модель, представься и очень коротко объясни как ты устроена"
    
    # Вариант 1: Без системного промпта
    stats1 = run_experiment(
        question=question,
        system_prompt="",
        temperature=0.7,
        role_name="Базовый ответ (без роли)"
    )
    time.sleep(2)  # Пауза между запросами
    
    # Вариант 2: Воспитатель с максимальной температурой
    stats2 = run_experiment(
        question=question,
        system_prompt="Ты - воспитатель старшей группы детского сада. Тебе нужно объяснить вопрос детям 5-7 лет",
        temperature=0.9,  # Почти максимум
        role_name="Воспитатель детсада (temp=1.8)"
    )
    time.sleep(2)
    
    # Вариант 3: Инженер с минимальной температурой
    stats3 = run_experiment(
        question=question,
        system_prompt="Ты - инженер-исследователь LLM с 20-летним стажем. Объясняешь коллегам",
        temperature=0.1,  # Минимум
        role_name="Инженер LLM (temp=0.1)"
    )
    
    # Финальное сравнение
    print("\n" + "="*70)
    print("📊 ИТОГОВОЕ СРАВНЕНИЕ")
    print("="*70)
    
    results = [stats1, stats2, stats3]
    
    print(f"""
    ┌─────────────────────┬───────────────────┬───────────────────┬───────────────────┐
    │    Характеристика   │   Базовый ответ   │   Воспитатель     │    Инженер        │
    ├─────────────────────┼───────────────────┼───────────────────┼───────────────────┤
    │ Длина (слова)       │ {stats1['length_words'] if stats1 else 0:<17} │ {stats2['length_words'] if stats2 else 0:<17} │ {stats3['length_words'] if stats3 else 0:<17} │
    │ Технических терминов│ {stats1['tech_terms'] if stats1 else 0:<17} │ {stats2['tech_terms'] if stats2 else 0:<17} │ {stats3['tech_terms'] if stats3 else 0:<17} │
    │ Детских маркеров    │ {stats1['child_markers'] if stats1 else 0:<17} │ {stats2['child_markers'] if stats2 else 0:<17} │ {stats3['child_markers'] if stats3 else 0:<17} │
    │ Английских слов     │ {stats1['english_loans'] if stats1 else 0:<17} │ {stats2['english_loans'] if stats2 else 0:<17} │ {stats3['english_loans'] if stats3 else 0:<17} │
    │ Восклицания/вопросы │ {stats1['exclamations'] if stats1 else 0}/{stats1['questions'] if stats1 else 0:<15} │ {stats2['exclamations'] if stats2 else 0}/{stats2['questions'] if stats2 else 0:<15} │ {stats3['exclamations'] if stats3 else 0}/{stats3['questions'] if stats3 else 0:<15} │
    └─────────────────────┴───────────────────┴───────────────────┴───────────────────┘
    """)
    
    # Вывод образцов для визуального сравнения
    print("\n📝 ОБРАЗЦЫ ОТВЕТОВ (первые 200 символов):")
    print(f"\n🔹 Базовый: {stats1['text_sample'] if stats1 else 'Нет данных'}")
    print(f"\n🔸 Воспитатель: {stats2['text_sample'] if stats2 else 'Нет данных'}")
    print(f"\n🔹 Инженер: {stats3['text_sample'] if stats3 else 'Нет данных'}")
