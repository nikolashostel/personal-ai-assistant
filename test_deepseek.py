from openai import OpenAI

from app.config.settings import settings

client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": "Что такое RAG? Ответь одним предложением."
        }
    ]
)

print(response.choices[0].message.content)