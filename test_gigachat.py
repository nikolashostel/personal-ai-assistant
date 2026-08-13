from gigachat import GigaChat
from app.config.settings import settings

with GigaChat(
    credentials=settings.GIGACHAT_CREDENTIALS,
    verify_ssl_certs=False,
) as giga:

    response = giga.chat(
        "Что такое RAG? Ответь одним коротким предложением."
    )

    print(response.choices[0].message.content)