import logging
from datetime import datetime

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.config.settings import settings
from app.running.schemas import RunningWorkoutData


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


TYPE, DATE, TIME, DURATION, DISTANCE, PACE, HEART_RATE, CADENCE, CONFIRM = range(9)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я Personal AI Assistant.\n\n"
        "Задай мне вопрос или используй /run, чтобы добавить беговую тренировку."
    )


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = (update.message.text or "").strip()

    if not question or not update.effective_user or not update.effective_chat:
        return

    user_id = str(update.effective_user.id)
    conversation_id = str(update.effective_chat.id)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ASSISTANT_API_URL.rstrip('/')}/ask",
                json={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "question": question,
                },
            )
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


def type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Обычная", callback_data="type:regular"),
                InlineKeyboardButton("Интервальная", callback_data="type:interval"),
            ]
        ]
    )


def date_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Сегодня", callback_data="date:today")]]
    )


def time_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Сейчас", callback_data="time:now")]]
    )


def confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Сохранить", callback_data="workout:save"),
                InlineKeyboardButton("✏️ Изменить", callback_data="workout:edit"),
            ],
            [InlineKeyboardButton("❌ Отмена", callback_data="workout:cancel")],
        ]
    )


def parse_duration(value: str) -> int | None:
    try:
        parts = value.strip().split(":")
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            if minutes < 0 or not 0 <= seconds < 60:
                return None
            return minutes * 60 + seconds
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            if hours < 0 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
                return None
            return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        return None
    return None


def parse_pace(value: str) -> int | None:
    try:
        minutes, seconds = map(int, value.strip().split(":"))
        if minutes < 0 or not 0 <= seconds < 60:
            return None
        return minutes * 60 + seconds
    except (ValueError, TypeError):
        return None


def parse_date(value: str):
    try:
        return datetime.strptime(value.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def parse_time(value: str):
    try:
        return datetime.strptime(value.strip(), "%H:%M").time()
    except ValueError:
        return None


async def run_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["workout"] = {}
    await update.message.reply_text(
        "🏃 Добавим тренировку.\n\nКакой тип тренировки?",
        reply_markup=type_keyboard(),
    )
    return TYPE


async def run_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    training_type = query.data.split(":", 1)[1]
    context.user_data["workout"]["training_type"] = training_type

    await query.edit_message_text(
        "📅 Какая дата?",
        reply_markup=date_keyboard(),
    )
    return DATE


async def run_date_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["workout"]["date"] = datetime.now().date()
    await query.edit_message_text(
        "🕐 Время начала?",
        reply_markup=time_keyboard(),
    )
    return TIME


async def run_date_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    date_value = parse_date(update.message.text)
    if date_value is None:
        await update.message.reply_text("Не понял дату. Введи в формате ДД.ММ.ГГГГ, например 25.08.2026.")
        return DATE

    context.user_data["workout"]["date"] = date_value
    await update.message.reply_text("🕐 Время начала?", reply_markup=time_keyboard())
    return TIME


async def run_time_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["workout"]["time"] = datetime.now().time().replace(second=0, microsecond=0)
    await query.edit_message_text("⏱ Длительность?\n\nВведи в формате мм:сс, например 44:31.")
    return DURATION


async def run_time_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    time_value = parse_time(update.message.text)
    if time_value is None:
        await update.message.reply_text("Не понял время. Введи в формате ЧЧ:ММ, например 07:42.")
        return TIME

    context.user_data["workout"]["time"] = time_value
    await update.message.reply_text("⏱ Длительность?\n\nВведи в формате мм:сс, например 44:31.")
    return DURATION


async def run_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = parse_duration(update.message.text)
    if duration is None:
        await update.message.reply_text("Не понял длительность. Введи, например 44:31.")
        return DURATION

    context.user_data["workout"]["duration_sec"] = duration
    await update.message.reply_text("📏 Дистанция, км?\n\nНапример: 8.03")
    return DISTANCE


async def run_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        distance = float(update.message.text.replace(",", ".").strip())
        if distance <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Не понял дистанцию. Введи число в километрах, например 8.03.")
        return DISTANCE

    context.user_data["workout"]["distance_km"] = distance
    await update.message.reply_text("🏃 Средний темп?\n\nВведи в формате мин:сек, например 5:32.")
    return PACE


async def run_pace(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pace = parse_pace(update.message.text)
    if pace is None or pace <= 0:
        await update.message.reply_text("Не понял темп. Введи в формате мин:сек, например 5:32.")
        return PACE

    context.user_data["workout"]["avg_pace_sec_km"] = pace
    await update.message.reply_text("❤️ Средний пульс?\n\nНапример: 151")
    return HEART_RATE


async def run_heart_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        heart_rate = int(update.message.text.strip())
        if heart_rate <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Не понял пульс. Введи целое число, например 151.")
        return HEART_RATE

    context.user_data["workout"]["avg_heart_rate"] = heart_rate
    await update.message.reply_text("🦶 Средний каденс?\n\nНапример: 171")
    return CADENCE


async def run_cadence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        cadence = int(update.message.text.strip())
        if cadence <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Не понял каденс. Введи целое число, например 171.")
        return CADENCE

    context.user_data["workout"]["avg_cadence"] = cadence

    workout = context.user_data["workout"]
    started_at = datetime.combine(workout["date"], workout["time"]).astimezone()

    try:
        validated = RunningWorkoutData(
            started_at=started_at,
            distance_km=workout["distance_km"],
            duration_sec=workout["duration_sec"],
            avg_pace_sec_km=workout["avg_pace_sec_km"],
            avg_heart_rate=workout["avg_heart_rate"],
            avg_cadence=workout["avg_cadence"],
            training_type=workout["training_type"],
        )
        context.user_data["validated_workout"] = validated
    except Exception:
        logger.exception("Workout validation failed")
        await update.message.reply_text("Не удалось проверить данные тренировки. Начни заново через /run.")
        return ConversationHandler.END

    type_label = "Обычная" if validated.training_type == "regular" else "Интервальная"
    await update.message.reply_text(
        "🏃 Проверь тренировку:\n\n"
        f"Тип: {type_label}\n"
        f"Дата: {validated.started_at.strftime('%d.%m.%Y')}\n"
        f"Время: {validated.started_at.strftime('%H:%M')}\n"
        f"Длительность: {format_duration(validated.duration_sec)}\n"
        f"Дистанция: {validated.distance_km} км\n"
        f"Средний темп: {format_pace(validated.avg_pace_sec_km)}/км\n"
        f"Средний пульс: {validated.avg_heart_rate} уд/мин\n"
        f"Средний каденс: {validated.avg_cadence} шаг/мин\n\n"
        "Всё верно?",
        reply_markup=confirmation_keyboard(),
    )
    return CONFIRM


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes}:{sec:02d}"


def format_pace(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"


async def run_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    action = query.data.split(":", 1)[1]

    if action == "cancel":
        context.user_data.pop("workout", None)
        context.user_data.pop("validated_workout", None)
        await query.edit_message_text("Тренировка отменена.")
        return ConversationHandler.END

    if action == "edit":
        context.user_data["workout"] = {}
        context.user_data.pop("validated_workout", None)
        await query.edit_message_text(
            "Начнём заново.\n\nКакой тип тренировки?",
            reply_markup=type_keyboard(),
        )
        return TYPE

    if action == "save":
        workout = context.user_data.get("validated_workout")
        if workout is None or not update.effective_user:
            await query.edit_message_text("Данные тренировки потеряны. Начни заново через /run.")
            return ConversationHandler.END

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.ASSISTANT_API_URL.rstrip('/')}/running/workouts",
                    json={
                        "user_id": str(update.effective_user.id),
                        "workout": workout.model_dump(mode="json"),
                    },
                )
                response.raise_for_status()
                data = response.json()

            await query.edit_message_text(
                f"✅ Тренировка сохранена. ID: {data['id']}"
            )
            context.user_data.pop("workout", None)
            context.user_data.pop("validated_workout", None)
            return ConversationHandler.END

        except httpx.HTTPError:
            logger.exception("Failed to save running workout")
            await query.edit_message_text(
                "Не удалось сохранить тренировку. Попробуй ещё раз."
            )
            return CONFIRM
        except Exception:
            logger.exception("Unexpected error while saving running workout")
            await query.edit_message_text(
                "Произошла ошибка при сохранении тренировки."
            )
            return CONFIRM

    return CONFIRM


def build_run_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("run", run_start)],
        states={
            TYPE: [CallbackQueryHandler(run_type, pattern=r"^type:")],
            DATE: [
                CallbackQueryHandler(run_date_button, pattern=r"^date:today$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, run_date_text),
            ],
            TIME: [
                CallbackQueryHandler(run_time_button, pattern=r"^time:now$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, run_time_text),
            ],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, run_duration)],
            DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, run_distance)],
            PACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, run_pace)],
            HEART_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, run_heart_rate)],
            CADENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, run_cadence)],
            CONFIRM: [CallbackQueryHandler(run_confirm, pattern=r"^workout:")],
        },
        fallbacks=[CommandHandler("run", run_start)],
        allow_reentry=True,
    )


def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set in the .env file"
        )

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(build_run_conversation())
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ask)
    )

    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
