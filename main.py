import logging
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import BOT_TOKEN
from database import Database
from handlers import (
    start_command, add_command, get_text, get_deadline, cancel_command,
    list_command, done_command, delete_command, remind_command, button_callback,
    TEXT, DEADLINE,
)
from scheduler import setup_scheduler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)


def main():
    db = Database()

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_command)],
        states={
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
            DEADLINE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline),
                CommandHandler("skip", get_deadline),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(conv)
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler("done", done_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(CommandHandler("remind", remind_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    setup_scheduler(app.bot, db)

    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()