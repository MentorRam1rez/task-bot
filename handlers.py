from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database import Database

db = Database()

TEXT, DEADLINE = range(2)

STATUS_ICON = {"active": "🔵", "done": "✅", "overdue": "🔴"}


# ── /start ──────────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Привіт, {name}! 👋 Я бот для управління твоїми задачами.\n\n"
        "📋 *Команди:*\n"
        "/add — додати задачу\n"
        "/list — всі активні задачі\n"
        "/list done — виконані\n"
        "/list overdue — прострочені\n"
        "/done `<id>` — позначити виконаною\n"
        "/delete `<id>` — видалити задачу\n"
        "/remind — задачі з дедлайном",
        parse_mode="Markdown",
    )


# ── /add ─────────────────────────────────────────────────────────────────────

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("✏️ Введи текст задачі:")
    return TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["task_text"] = update.message.text
    await update.message.reply_text(
        "📅 Введи дедлайн у форматі `ДД.ММ.РРРР ГГ:ХХ`\n"
        "або /skip щоб пропустити.",
        parse_mode="Markdown",
    )
    return DEADLINE


async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    deadline = None

    if text != "/skip":
        try:
            deadline = datetime.strptime(text, "%d.%m.%Y %H:%M")
        except ValueError:
            await update.message.reply_text(
                "❌ Невірний формат. Спробуй ще раз: `ДД.ММ.РРРР ГГ:ХХ`",
                parse_mode="Markdown",
            )
            return DEADLINE

    user_id = update.effective_user.id
    task_id = db.add_task(user_id, context.user_data["task_text"], deadline)

    dl_str = deadline.strftime("%d.%m.%Y %H:%M") if deadline else "без дедлайну"
    await update.message.reply_text(
        f"✅ Задачу *#{task_id}* додано!\n📌 Дедлайн: {dl_str}",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Скасовано.")
    return ConversationHandler.END


# ── /list ────────────────────────────────────────────────────────────────────

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    filter_arg = context.args[0] if context.args else "active"

    valid = {"active", "done", "overdue", "all"}
    if filter_arg not in valid:
        await update.message.reply_text("Фільтр: active | done | overdue | all")
        return

    tasks = db.get_tasks(user_id, status=filter_arg)
    if not tasks:
        await update.message.reply_text("😌 Задач не знайдено.")
        return

    lines = []
    for t in tasks:
        icon = STATUS_ICON.get(t.status, "⬜")
        dl = t.deadline.strftime("%d.%m %H:%M") if t.deadline else "—"
        lines.append(f"{icon} *#{t.id}* {t.text}\n   ⏰ {dl}")

    keyboard = [
        [InlineKeyboardButton(f"✅ Виконано #{t.id}", callback_data=f"done_{t.id}")]
        for t in tasks if t.status == "active"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    await update.message.reply_text(
        "\n\n".join(lines),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


# ── /done ────────────────────────────────────────────────────────────────────

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Використання: /done `<id>`", parse_mode="Markdown")
        return
    task_id = int(context.args[0])
    if db.mark_done(user_id, task_id):
        await update.message.reply_text(f"✅ Задачу *#{task_id}* виконано!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Задачу не знайдено або вона вже виконана.")


# ── /delete ──────────────────────────────────────────────────────────────────

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Використання: /delete `<id>`", parse_mode="Markdown")
        return
    task_id = int(context.args[0])
    if db.delete_task(user_id, task_id):
        await update.message.reply_text(f"🗑 Задачу *#{task_id}* видалено.", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Задачу не знайдено.")


# ── /remind ──────────────────────────────────────────────────────────────────

async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tasks = [t for t in db.get_tasks(user_id, "active") if t.deadline]
    if not tasks:
        await update.message.reply_text("😌 Немає активних задач із дедлайном.")
        return
    lines = [
        f"⏰ *#{t.id}* {t.text}\n   📅 {t.deadline.strftime('%d.%m.%Y %H:%M')}"
        for t in tasks
    ]
    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")


# ── Callback (інлайн-кнопки) ─────────────────────────────────────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("done_"):
        task_id = int(query.data.split("_")[1])
        user_id = query.from_user.id
        if db.mark_done(user_id, task_id):
            await query.edit_message_text(
                query.message.text + f"\n\n✅ Задачу #{task_id} виконано!",
                parse_mode="Markdown",
            )
        else:
            await query.answer("Задачу не знайдено або вже виконана.", show_alert=True)