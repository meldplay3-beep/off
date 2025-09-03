import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Логи
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WOODPICKER_API_KEY = os.getenv("WOODPICKER_API_KEY")
if not TELEGRAM_TOKEN or not WOODPICKER_API_KEY:
    raise SystemExit("TELEGRAM_TOKEN и WOODPICKER_API_KEY должны быть установлены в переменных окружения")

# Хранилище имен пользователей
users = {}

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет 🌿 Я твой дружелюбный помощник. Как мне к тебе обращаться?")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = " ".join(context.args)
    if name:
        users[user_id] = name
        await update.message.reply_text(f"Отлично, буду обращаться к тебе {name} 🌸")
    else:
        await update.message.reply_text("Напиши имя после команды /setname Имя")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хорошо, делаем паузу 🌿")

# Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = users.get(user_id, "друг")
    user_text = update.message.text

    prompt = f"""
Ты дружелюбный AI-друг.
Помогаешь человеку успокоиться после ссоры, мягко разбираешь ситуацию и ведешь к примирению.
Обращайся по имени {user_name}.
Пользователь пишет: "{user_text}"
Дай поддержку и советы для примирения.
"""

    try:
        response = requests.post(
            "https://api.woodpicker.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {WOODPICKER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 500
            }
        )
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"WoodPicker API error: {e}")
        await update.message.reply_text("Упс, что-то пошло не так 😅 Попробуй через минуту.")

# Запуск бота (Background Worker)
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setname", set_name))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running as Background Worker...")
    app.run_polling()

if __name__ == "__main__":
    main()