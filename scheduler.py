from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz
from database import Database

TZ = pytz.timezone("Europe/Kyiv")


async def check_reminders(bot, db: Database):
    from language import t
    now = datetime.now(TZ)
    tasks = db.get_upcoming_tasks(
        from_dt=now + timedelta(minutes=55),
        to_dt=now + timedelta(minutes=65),
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
    from ai_helper import morning_ai_message
    users = db.get_all_users()
    now = datetime.now(TZ)
    today_end = now.replace(hour=23, minute=59)

    for user_id in users:
        try:
            chat = await bot.get_chat(user_id)
            name = chat.first_name or "друже"
            # Задачі на сьогодні
            tasks = [
                t for t in db.get_tasks(user_id, "active")
                if t.deadline and now <= t.deadline.replace(tzinfo=TZ) <= today_end
            ]
            msg = morning_ai_message(name, tasks)
            await bot.send_message(chat_id=user_id, text=f"🌅 {msg}")
        except Exception as e:
            print(f"Morning greeting error for {user_id}: {e}")


async def daytime_check(bot, db: Database):
    """Перевіряє задачі на найближчі 3 години і нагадує."""
    from ai_helper import daytime_reminder_message
    users = db.get_all_users()
    now = datetime.now(TZ)
    in_3h = now + timedelta(hours=3)

    for user_id in users:
        try:
            tasks = [
                t for t in db.get_tasks(user_id, "active")
                if t.deadline and now <= t.deadline.replace(tzinfo=TZ) <= in_3h
            ]
            if not tasks:
                continue
            chat = await bot.get_chat(user_id)
            name = chat.first_name or "друже"
            msg = daytime_reminder_message(name, tasks)
            await bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            print(f"Daytime check error for {user_id}: {e}")


async def evening_analysis(bot, db: Database):
    """Вечірній AI аналіз дня о 21:00."""
    from ai_helper import evening_analysis_message
    users = db.get_all_users()

    for user_id in users:
        try:
            stats = db.get_stats(user_id)
            chat = await bot.get_chat(user_id)
            name = chat.first_name or "друже"
            msg = evening_analysis_message(
                name,
                done=stats["done"],
                active=stats["active"],
                overdue=stats["overdue"],
            )
            await bot.send_message(chat_id=user_id, text=f"🌙 {msg}")
        except Exception as e:
            print(f"Evening analysis error for {user_id}: {e}")


def setup_scheduler(bot, db: Database) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

    # Щохвилинна перевірка нагадувань за годину до дедлайну
    scheduler.add_job(
        check_reminders, trigger="interval", minutes=1,
        args=[bot, db], id="reminder_check", replace_existing=True,
    )

    # Ранкове привітання о 09:00
    scheduler.add_job(
        morning_greeting, trigger="cron", hour=9, minute=0,
        args=[bot, db], id="morning_greeting", replace_existing=True,
    )

    # Денна перевірка кожні 2 години (11, 13, 15, 17, 19)
    scheduler.add_job(
        daytime_check, trigger="cron", hour="11,13,15,17,19", minute=0,
        args=[bot, db], id="daytime_check", replace_existing=True,
    )

    # Вечірній аналіз о 21:00
    scheduler.add_job(
        evening_analysis, trigger="cron", hour=21, minute=0,
        args=[bot, db], id="evening_analysis", replace_existing=True,
    )

    scheduler.start()
    return scheduler