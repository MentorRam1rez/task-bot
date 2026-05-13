from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database


async def check_reminders(bot, db: Database):
    now = datetime.now()
    tasks = db.get_upcoming_tasks(
        from_dt=now + timedelta(minutes=55),
        to_dt=now + timedelta(minutes=65),
    )
    for task in tasks:
        dl_str = task.deadline.strftime("%d.%m.%Y %H:%M")
        await bot.send_message(
            chat_id=task.user_id,
            text=(
                f"⏰ *Нагадування!*\n"
                f"Через ~1 годину дедлайн задачі:\n\n"
                f"*#{task.id}* {task.text}\n"
                f"📅 {dl_str}"
            ),
            parse_mode="Markdown",
        )
        db.log_reminder(task.id)

    db.mark_overdue()


async def check_reminders_wrapper(bot, db):
    await check_reminders(bot, db)


def setup_scheduler(bot, db: Database) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_reminders,
        trigger="interval",
        minutes=1,
        args=[bot, db],
        id="reminder_check",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler