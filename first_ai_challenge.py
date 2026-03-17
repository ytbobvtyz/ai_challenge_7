
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# 2. Создаем клиент, но указываем адрес OpenRouter и свой ключ
#    Ключ нужно сохранить в переменной окружения OPENROUTER_API_KEY
#    (подробнее как это сделать для своей ОС - в комментариях кода ниже)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # Единый шлюз OpenRouter
    api_key=os.environ.get("OPENROUTER_API_KEY"),  # Твой единственный ключ
    default_headers={
        "HTTP-Referer": "http://localhost:8000",  # Можно указать свой сайт или приложение
        "X-Title": "My First AI Adventure",  # Название твоего проекта
    }
)

# 3. Функция для общения с AI
def ask_ai(user_question):
    """Отправляет вопрос в OpenRouter и печатает ответ."""
    print(f"\n🤔 Задаю вопрос: {user_question}")

    try:
        # Отправляем запрос. Модель можно поменять на любую из списка!
        completion = client.chat.completions.create(
            model="stepfun/step-3.5-flash:free",  #  "google/gemini-2.0-flash-exp:free" или "deepseek/deepseek-chat"
            messages=[
                {"role": "user", "content": user_question}
            ],
            max_tokens=2000
        )

        # 4. Получаем и выводим ответ
        answer = completion.choices[0].message.content
        print(f"🤖 Ответ от ИИ:\n{answer}\n")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

# 5. Запускаем
if __name__ == "__main__":
    # Простой тестовый вопрос
    ask_ai("Модель, назови себя и свои возможные параметры настроек!")