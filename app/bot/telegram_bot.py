import logging

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config.settings import settings


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8000/ask"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я Enterprise AI Knowledge Assistant.\n\n"
        "Задай вопрос по корпоративной базе знаний."
    )


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = (update.message.text or "").strip()

    if not question:
        return

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(API_URL, json={"question": question})
            response.raise_for_status()
            data = response.json()

        await update.message.reply_text(data["answer"])

    except httpx.HTTPError:
        logger.exception("Failed to call FastAPI")
        await update.message.reply_text(
            "Не удалось получить ответ от AI-сервиса. Попробуй ещё раз."
        )
    except Exception:
        logger.exception("Unexpected Telegram bot error")
        await update.message.reply_text(
            "Произошла ошибка. Попробуй ещё раз."
        )


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set in the .env file"
        )

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ask)
    )

    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
