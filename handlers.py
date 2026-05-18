from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database import Database
from language import t

db = Database()

TEXT, DEADLINE, PRIORITY, CATEGORY, REPEAT, REPEAT_DAYS = range(6)

STATUS_ICON = {"active": "🔵", "done": "✅", "overdue": "🔴"}
PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
CATEGORY_ICON = {"work": "💼", "study": "📚", "personal": "🏠", None: "📌"}


def lang(user_id: int) -> str:
    return db.get_language(user_id)

#/start

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    l = lang(user.id)
    await update.message.reply_text(
        t(l, "welcome", name=user.first_name),
        parse_mode="Markdown",
    )

#/help

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update.effective_user.id)
    await update.message.reply_text(t(l, "help_title"), parse_mode="Markdown")
#/lang

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    l = lang(update.effective_user.id)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ])
    await update.message.reply_text(t(l, "choose_lang"), reply_markup=keyboard)

#/add

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    l = lang(update.effective_user.id)
    await update.message.reply_text(t(l, "enter_text"))
    return TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    l = lang(update.effective_user.id)
    context.user_data["task_text"] = update.message.text
    await update.message.reply_text(t(l, "enter_deadline"), parse_mode="Markdown")
    return DEADLINE


async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    l = lang(update.effective_user.id)
    text = update.message.text
    deadline = None

    if text != "/skip":
        try:
            deadline = datetime.strptime(text, "%d.%m.%Y %H:%M")
        except ValueError:
            await update.message.reply_text(t(l, "invalid_format"), parse_mode="Markdown")
            return DEADLINE

    context.user_data["deadline"] = deadline

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(l, "priority_high"), callback_data="priority_high"),
            InlineKeyboardButton(t(l, "priority_medium"), callback_data="priority_medium"),
            InlineKeyboardButton(t(l, "priority_low"), callback_data="priority_low"),
        ]
    ])
    await update.message.reply_text(t(l, "choose_priority"), reply_markup=keyboard)
    return PRIORITY


async def get_priority(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    l = lang(query.from_user.id)

    priority = query.data.replace("priority_", "")
    context.user_data["priority"] = priority

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(l, "category_work"), callback_data="cat_work"),
            InlineKeyboardButton(t(l, "category_study"), callback_data="cat_study"),
        ],
        [
            InlineKeyboardButton(t(l, "category_personal"), callback_data="cat_personal"),
            InlineKeyboardButton(t(l, "category_none"), callback_data="cat_none"),
        ]
    ])
    await query.edit_message_text(t(l, "choose_category"), reply_markup=keyboard)
    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    l = lang(query.from_user.id)

    category = query.data.replace("cat_", "")
    context.user_data["category"] = None if category == "none" else category

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t(l, "repeat_none"), callback_data="repeat_none"),
            InlineKeyboardButton(t(l, "repeat_daily"), callback_data="repeat_daily"),
        ],
        [
            InlineKeyboardButton(t(l, "repeat_custom"), callback_data="repeat_custom"),
        ]
    ])
    await query.edit_message_text(t(l, "choose_repeat"), reply_markup=keyboard)
    return REPEAT


async def get_repeat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    l = lang(query.from_user.id)

    repeat = query.data.replace("repeat_", "")

    if repeat == "none":
        context.user_data["repeat_type"] = None
        context.user_data["repeat_days"] = None
        return await _save_task(query, context, l)
    elif repeat == "daily":
        context.user_data["repeat_type"] = "daily"
        context.user_data["repeat_days"] = None
        return await _save_task(query, context, l)
    else:
        context.user_data["repeat_type"] = "custom"
        context.user_data["repeat_days"] = []
        days = t(l, "days")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(days[i], callback_data=f"day_{i}") for i in range(7)],
            [InlineKeyboardButton(t(l, "confirm_days"), callback_data="days_confirm")]
        ])
        await query.edit_message_text(t(l, "choose_repeat_days"), reply_markup=keyboard)
        return REPEAT_DAYS


async def get_repeat_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    l = lang(query.from_user.id)

    if query.data == "days_confirm":
        days = context.user_data.get("repeat_days", [])
        context.user_data["repeat_days"] = ",".join(map(str, days))
        return await _save_task(query, context, l)

    day = int(query.data.replace("day_", ""))
    days = context.user_data.get("repeat_days", [])
    if day in days:
        days.remove(day)
    else:
        days.append(day)
    context.user_data["repeat_days"] = days

    day_names = t(l, "days")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{'✅' if i in days else ''}{day_names[i]}",
            callback_data=f"day_{i}"
        ) for i in range(7)],
        [InlineKeyboardButton(t(l, "confirm_days"), callback_data="days_confirm")]
    ])
    await query.edit_message_text(t(l, "choose_repeat_days"), reply_markup=keyboard)
    return REPEAT_DAYS


async def _save_task(query, context, l: str) -> int:
    user_id = query.from_user.id
    deadline = context.user_data.get("deadline")
    priority = context.user_data.get("priority", "medium")
    category = context.user_data.get("category")
    repeat_type = context.user_data.get("repeat_type")
    repeat_days = context.user_data.get("repeat_days")

    task_id = db.add_task(
        user_id=user_id,
        text=context.user_data["task_text"],
        deadline=deadline,
        priority=priority,
        category=category,
        repeat_type=repeat_type,
        repeat_days=repeat_days if isinstance(repeat_days, str) else None,
    )

    priority_labels = {"high": t(l, "priority_high"), "medium": t(l, "priority_medium"), "low": t(l, "priority_low")}
    category_labels = {"work": t(l, "category_work"), "study": t(l, "category_study"), "personal": t(l, "category_personal"), None: t(l, "category_none")}

    dl_str = deadline.strftime("%d.%m.%Y %H:%M") if deadline else t(l, "no_deadline")
    await query.edit_message_text(
        t(l, "task_added", id=task_id, deadline=dl_str,
          priority=priority_labels.get(priority, priority),
          category=category_labels.get(category, "")),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    l = lang(update.effective_user.id)
    await update.message.reply_text(t(l, "cancelled"))
    return ConversationHandler.END

#/list

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    l = lang(user_id)
    filter_arg = context.args[0] if context.args else "active"

    valid_status = {"active", "done", "overdue", "all"}
    valid_priority = {"high", "medium", "low"}

    if filter_arg in valid_priority:
        tasks = db.get_tasks_by_priority(user_id, priority=filter_arg)
    elif filter_arg in valid_status:
        tasks = db.get_tasks(user_id, status=filter_arg)
    else:
        await update.message.reply_text(t(l, "filter_hint"))
        return

    if not tasks:
        await update.message.reply_text(t(l, "no_tasks"))
        return

    lines = []
    for task in tasks:
        status_icon = STATUS_ICON.get(task.status, "⬜")
        priority_icon = PRIORITY_ICON.get(task.priority, "🟡")
        category_icon = CATEGORY_ICON.get(task.category, "📌")
        dl = task.deadline.strftime("%d.%m %H:%M") if task.deadline else "—"
        repeat = " 🔄" if task.repeat_type else ""
        lines.append(
            f"{status_icon}{priority_icon}{category_icon} *#{task.id}* {task.text}{repeat}\n   ⏰ {dl}"
        )

    keyboard = [
        [InlineKeyboardButton(t(l, "done_btn", id=task.id), callback_data=f"done_{task.id}")]
        for task in tasks if task.status == "active"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        "\n\n".join(lines),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

#/done

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    l = lang(user_id)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(t(l, "use_id", cmd="done"), parse_mode="Markdown")
        return
    task_id = int(context.args[0])
    if db.mark_done(user_id, task_id):
        await update.message.reply_text(t(l, "task_done", id=task_id), parse_mode="Markdown")
    else:
        await update.message.reply_text(t(l, "task_already_done"))

#/delete

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    l = lang(user_id)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(t(l, "use_id", cmd="delete"), parse_mode="Markdown")
        return
    task_id = int(context.args[0])
    if db.delete_task(user_id, task_id):
        await update.message.reply_text(t(l, "task_deleted", id=task_id), parse_mode="Markdown")
    else:
        await update.message.reply_text(t(l, "task_not_found"))

#/remind

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    l = lang(user_id)
    tasks = [task for task in db.get_tasks(user_id, "active") if task.deadline]
    if not tasks:
        await update.message.reply_text(t(l, "no_deadline_tasks"))
        return
    lines = [
        f"⏰ *#{task.id}* {task.text}\n   📅 {task.deadline.strftime('%d.%m.%Y %H:%M')}"
        for task in tasks
    ]
    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")

#/stats

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    l = lang(user_id)
    stats = db.get_stats(user_id)
    await update.message.reply_text(
        t(l, "stats_title", **stats),
        parse_mode="Markdown",
    )

#Callback

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    l = lang(query.from_user.id)

    if query.data.startswith("lang_"):
        lang_code = query.data.replace("lang_", "")
        db.set_language(query.from_user.id, lang_code)
        await query.answer()
        await query.edit_message_text(t(lang_code, "lang_set"))

    elif query.data.startswith("done_"):
        await query.answer()
        task_id = int(query.data.split("_")[1])
        user_id = query.from_user.id
        if db.mark_done(user_id, task_id):
            await query.edit_message_text(
                query.message.text + f"\n\n✅ #{task_id}",
                parse_mode="Markdown",
            )
        else:
            await query.answer(t(l, "task_already_done"), show_alert=True)