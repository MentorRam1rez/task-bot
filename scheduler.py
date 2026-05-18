from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from database import Database
import pytz

async def check_reminders(bot, db: Database):
    from language import t
    tz = pytz.timezone("Europe/Kyiv")
    now_local = datetime.now(tz)

    tasks = db.get_upcoming_tasks(
        from_dt=now_local + timedelta(minutes=55),
        to_dt=now_local + timedelta(minutes=65),
    )
    for task in tasks:
        try:
            l = db.get_language(task.user_id)
            dl_str = task.deadline.strftime("%d.%m.%Y %H:%M")
            await bot.send_message(
                chat_id=task.user_id,
                text=t(l, "reminder_text", id=task.id, text=task.text, deadline=dl_str),
                parse_mode="Markdown",
            )
            db.log_reminder(task.id)
        except Exception as e:
            print(f"Reminder error: {e}")
    db.mark_overdue()


async def morning_greeting(bot, db: Database):
    from language import t
    users = db.get_all_users()
    for user_id in users:
        try:
            l = db.get_language(user_id)
            # Беремо нікнейм з Telegram
            chat = await bot.get_chat(user_id)
            name = chat.first_name or chat.username or "друже"
            await bot.send_message(
                chat_id=user_id,
                text=t(l, "morning_greeting", name=name),
                parse_mode="Markdown",
            )
        except Exception:
            pass  # якщо користувач заблокував бота — пропускаємо


def setup_scheduler(bot, db: Database) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

    scheduler.add_job(
        check_reminders,
        trigger="interval",
        minutes=1,
        args=[bot, db],
        id="reminder_check",
        replace_existing=True,
    )

    scheduler.add_job(
        morning_greeting,
        trigger="cron",
        hour=9,
        minute=0,
        args=[bot, db],
        id="morning_greeting",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler