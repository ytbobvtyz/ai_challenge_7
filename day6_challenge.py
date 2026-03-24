# day6_agent.py

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SimpleAgent:
    """
    Простой агент для общения с LLM через OpenRouter.
    Инкапсулирует логику вызова API, историю диалога и обработку ошибок.
    """
    
    def __init__(self, model="stepfun/step-3.5-flash:free", system_prompt=None, max_history=20):
        """
        Инициализация агента.
        
        Args:
            model: идентификатор модели в OpenRouter
            system_prompt: системный промпт (задаёт роль агента)
            max_history: максимальное количество сообщений в истории
        """
        self.model = model
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.history = []  # хранит сообщения в формате [{"role": "user/assistant", "content": "..."}]
        
        # Инициализация клиента OpenAI (совместим с OpenRouter)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "AI Challenge Day 6 - Simple Agent"
            }
        )
        
        # Если задан системный промпт, добавляем его в начало истории
        if self.system_prompt:
            self.history.append({"role": "system", "content": self.system_prompt})
    
    def think(self, user_input):
        """
        Обработать запрос пользователя и вернуть ответ агента.
        
        Args:
            user_input: строка с запросом пользователя
            
        Returns:
            строка с ответом агента или None в случае ошибки
        """
        if not user_input or not user_input.strip():
            return "❌ Пустой запрос. Напиши что-нибудь!"
        
        # Добавляем запрос пользователя в историю
        self.history.append({"role": "user", "content": user_input})
        
        # Ограничиваем историю, чтобы не превысить контекст
        self._trim_history()
        
        try:
            # Формируем сообщения для API (история уже содержит system и user)
            messages = self.history.copy()
            
            # Вызываем API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            # Извлекаем ответ
            agent_response = response.choices[0].message.content
            
            # Добавляем ответ в историю
            self.history.append({"role": "assistant", "content": agent_response})
            
            return agent_response
            
        except Exception as e:
            error_msg = f"❌ Ошибка при вызове API: {str(e)}"
            print(error_msg)  # Печатаем в консоль для отладки
            return error_msg
    
    def _trim_history(self):
        """
        Обрезает историю, оставляя последние max_history сообщений.
        Системный промпт (если есть) всегда сохраняется.
        """
        if len(self.history) > self.max_history:
            # Сохраняем системный промпт, если он есть
            if self.system_prompt and self.history[0]["role"] == "system":
                system_msg = self.history[0]
                # Оставляем системный промпт + последние max_history-1 сообщений
                self.history = [system_msg] + self.history[-(self.max_history - 1):]
            else:
                self.history = self.history[-self.max_history:]
    
    def reset(self):
        """Очищает историю диалога, сохраняя системный промпт."""
        self.history = []
        if self.system_prompt:
            self.history.append({"role": "system", "content": self.system_prompt})
        print("🧹 История диалога очищена.")
    
    def get_history(self):
        """Возвращает историю диалога для отладки."""
        return self.history.copy()
    
    def save_history(self, filename=None):
        """Сохраняет историю диалога в файл."""
        if not filename:
            filename = f"agent_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        print(f"💾 История сохранена в {filename}")
        return filename


def run_cli_agent():
    """Запускает агента в режиме командной строки (CLI)."""
    
    print("\n" + "="*60)
    print("🤖 AI АГЕНТ — ДЕНЬ 6")
    print("="*60)
    print("\nДоступные команды:")
    print("  /reset  — очистить историю диалога")
    print("  /save   — сохранить историю в файл")
    print("  /exit   — выйти из программы")
    print("  /help   — показать эту справку")
    print("\n" + "-"*60)
    
    # Создаём агента с интересным системным промптом
    agent = SimpleAgent(
        model="stepfun/step-3.5-flash:free",
        system_prompt=(
            "Ты — джедай-программист по имени Дип. Отвечаешь мудро, с юмором, но всегда очень коротко"
            "используешь аналогии из мира Звёздных Войн. Помогаешь пользователю "
            "разбираться в AI и программировании. Если пользователь просит код — "
            "отвечаешь, что только путь указываешь ты и даёшь краткую наводку что поизучать, но не код. ЗАПРЕЩЕНО ДАВАТЬ ГОТОВЫЙ КОД"
        )
    )
    
    print(f"\n🤖 Агент инициализирован. Модель: {agent.model}")
    print(f"📜 Системный промпт: {agent.system_prompt[:100]}...\n")
    
    while True:
        try:
            # Получаем ввод пользователя
            user_input = input("\n👤 Вы: ").strip()
            
            if not user_input:
                continue
            
            # Обработка команд
            if user_input.lower() == '/exit':
                print("\n🤖 Май-да будет с тобой сила! До встречи!")
                break
            elif user_input.lower() == '/reset':
                agent.reset()
                continue
            elif user_input.lower() == '/save':
                agent.save_history()
                continue
            elif user_input.lower() == '/help':
                print("\nДоступные команды:")
                print("  /reset  — очистить историю диалога")
                print("  /save   — сохранить историю в файл")
                print("  /exit   — выйти из программы")
                print("  /help   — показать эту справку")
                continue
            
            # Отправляем запрос агенту и получаем ответ
            print("\n🤖 Агент: ", end="", flush=True)
            response = agent.think(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n🤖 Прервано пользователем. Да пребудет с тобой сила!")
            break
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")


def run_single_query_example():
    """Пример использования агента для одного запроса (без цикла)."""
    
    print("\n" + "="*60)
    print("🤖 ПРИМЕР: Одиночный запрос к агенту")
    print("="*60)
    
    agent = SimpleAgent(
        model="stepfun/step-3.5-flash:free",
        system_prompt="Ты — эксперт по Python, отвечаешь кратко и по делу."
    )
    
    query = "Напиши простую функцию на Python, которая проверяет, является ли число простым."
    
    print(f"\n👤 Запрос: {query}")
    print("\n🤖 Ответ агента:")
    print("-"*60)
    
    response = agent.think(query)
    print(response)
    
    print("-"*60)
    print("\n📜 История диалога:")
    for msg in agent.get_history():
        print(f"  {msg['role']}: {msg['content'][:100]}...")


if __name__ == "__main__":
    print("\n" + "🎯"*35)
    print("🎯 ДЕНЬ 6: ПЕРВЫЙ АГЕНТ")
    print("🎯"*35)
    
    print("\nВыбери режим:")
    print("  1. CLI-чат (интерактивный диалог)")
    print("  2. Одиночный запрос (демонстрация)")
    
    choice = input("\n👉 Твой выбор (1/2): ").strip()
    
    if choice == "1":
        run_cli_agent()
    elif choice == "2":
        run_single_query_example()
    else:
        print("❌ Неверный выбор. Запускаю CLI-чат по умолчанию.")
        run_cli_agent()