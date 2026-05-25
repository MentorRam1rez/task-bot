TEXTS = {
    "uk": {
        "welcome": "Привіт, {name}! 👋 Я бот для управління твоїми задачами.\n\n📋 *Команди:*\n/add — додати задачу\n/list — всі активні задачі\n/list done — виконані\n/list overdue — прострочені\n/done `<id>` — позначити виконаною\n/delete `<id>` — видалити задачу\n/remind — задачі з дедлайном\n/stats — статистика\n/lang — змінити мову\n/ai — AI-помічник\n/help — довідка",
        "choose_lang": "🌍 Оберіть мову / Choose language:",
        "lang_set": "✅ Мову встановлено: Українська 🇺🇦",
        "enter_text": "✏️ Введи текст задачі:",
        "enter_deadline": "📅 Введи дедлайн у форматі `ДД.ММ.РРРР ГГ:ХХ`\nабо /skip щоб пропустити.",
        "choose_priority": "🎯 Оберіть пріоритет задачі:",
        "choose_category": "📂 Оберіть категорію задачі:",
        "choose_repeat": "🔄 Повторення задачі:",
        "choose_repeat_days": "📅 Оберіть дні повторення:",
        "task_added": "✅ Задачу *#{id}* додано!\n📌 Дедлайн: {deadline}\n🎯 Пріоритет: {priority}\n📂 Категорія: {category}",
        "no_tasks": "😌 Задач не знайдено.",
        "cancelled": "❌ Скасовано.",
        "invalid_format": "❌ Невірний формат. Спробуй ще раз: `ДД.ММ.РРРР ГГ:ХХ`",
        "task_done": "✅ Задачу *#{id}* виконано!",
        "task_deleted": "🗑 Задачу *#{id}* видалено.",
        "task_not_found": "❌ Задачу не знайдено.",
        "task_already_done": "❌ Задачу не знайдено або вона вже виконана.",
        "no_deadline_tasks": "😌 Немає активних задач із дедлайном.",
        "filter_hint": "Фільтр: active | done | overdue | all | high | medium | low",
        "done_btn": "✅ Виконано #{id}",
        "no_deadline": "без дедлайну",
        "reminder_text": "⏰ *Нагадування!*\nЧерез ~1 годину дедлайн задачі:\n\n*#{id}* {text}\n📅 {deadline}",
        "stats_title": "📊 *Твоя статистика:*\n\n✅ Виконано: {done}\n🔵 Активних: {active}\n🔴 Прострочених: {overdue}\n📝 Всього: {total}\n🏆 Відсоток виконання: {percent}%",
        "priority_high": "🔴 Високий",
        "priority_medium": "🟡 Середній",
        "priority_low": "🟢 Низький",
        "category_work": "💼 Робота",
        "category_study": "📚 Навчання",
        "category_personal": "🏠 Особисте",
        "category_none": "📌 Без категорії",
        "repeat_none": "❌ Без повторення",
        "repeat_daily": "🔄 Щодня",
        "repeat_custom": "📅 Певні дні",
        "days": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
        "confirm_days": "✅ Підтвердити дні",
        "use_id": "Використання: /{cmd} `<id>`",
        "morning_greeting": "🌅 Доброго ранку, {name}!\n\nЯкі на сьогодні плани? Не забудь перевірити свої задачі!\n\n/list — переглянути задачі\n/add — додати нову",
        "help_title": (
            "📖 *Довідка по боту*\n\n"
            "➕ *Додавання задач*\n"
            "/add — додати нову задачу (текст, дедлайн, пріоритет, категорія, повторення)\n\n"
            "📋 *Перегляд задач*\n"
            "/list — активні задачі\n"
            "/list done — виконані\n"
            "/list overdue — прострочені\n"
            "/list all — всі задачі\n"
            "/list high — високий пріоритет 🔴\n"
            "/list medium — середній пріоритет 🟡\n"
            "/list low — низький пріоритет 🟢\n\n"
            "✅ *Керування задачами*\n"
            "/done `<id>` — позначити виконаною\n"
            "/delete `<id>` — видалити задачу\n\n"
            "⏰ *Нагадування*\n"
            "/remind — задачі з дедлайном\n"
            "Бот автоматично нагадує за 1 годину до дедлайну\n\n"
            "🤖 *AI-асистент*\n"
            "/ai — запустити AI-помічника\n"
            "AI аналізує твої задачі і дає поради.\n"
            "Просто напиши йому:\n"
            "/aiend — завершити розмову з AI\n\n"
            "📊 *Інше*\n"
            "/stats — статистика виконання\n"
            "/lang — змінити мову\n"
            "/help — ця довідка\n\n"
            "💡 *Підказка:* Після /add бот проведе тебе крок за кроком!"
        ),
    },
    "en": {
        "welcome": "Hi, {name}! 👋 I'm your task management bot.\n\n📋 *Commands:*\n/add — add a task\n/list — all active tasks\n/list done — completed\n/list overdue — overdue\n/done `<id>` — mark as done\n/delete `<id>` — delete task\n/remind — tasks with deadlines\n/stats — statistics\n/lang — change language\n/ai — AI assistant\n/help — help",
        "choose_lang": "🌍 Оберіть мову / Choose language:",
        "lang_set": "✅ Language set: English 🇬🇧",
        "enter_text": "✏️ Enter task text:",
        "enter_deadline": "📅 Enter deadline in format `DD.MM.YYYY HH:MM`\nor /skip to skip.",
        "choose_priority": "🎯 Choose task priority:",
        "choose_category": "📂 Choose task category:",
        "choose_repeat": "🔄 Task repetition:",
        "choose_repeat_days": "📅 Choose repeat days:",
        "task_added": "✅ Task *#{id}* added!\n📌 Deadline: {deadline}\n🎯 Priority: {priority}\n📂 Category: {category}",
        "no_tasks": "😌 No tasks found.",
        "cancelled": "❌ Cancelled.",
        "invalid_format": "❌ Invalid format. Try again: `DD.MM.YYYY HH:MM`",
        "task_done": "✅ Task *#{id}* marked as done!",
        "task_deleted": "🗑 Task *#{id}* deleted.",
        "task_not_found": "❌ Task not found.",
        "task_already_done": "❌ Task not found or already completed.",
        "no_deadline_tasks": "😌 No active tasks with deadlines.",
        "filter_hint": "Filter: active | done | overdue | all | high | medium | low",
        "done_btn": "✅ Done #{id}",
        "no_deadline": "no deadline",
        "reminder_text": "⏰ *Reminder!*\nDeadline in ~1 hour:\n\n*#{id}* {text}\n📅 {deadline}",
        "stats_title": "📊 *Your statistics:*\n\n✅ Completed: {done}\n🔵 Active: {active}\n🔴 Overdue: {overdue}\n📝 Total: {total}\n🏆 Completion rate: {percent}%",
        "priority_high": "🔴 High",
        "priority_medium": "🟡 Medium",
        "priority_low": "🟢 Low",
        "category_work": "💼 Work",
        "category_study": "📚 Study",
        "category_personal": "🏠 Personal",
        "category_none": "📌 No category",
        "repeat_none": "❌ No repeat",
        "repeat_daily": "🔄 Daily",
        "repeat_custom": "📅 Custom days",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "confirm_days": "✅ Confirm days",
        "use_id": "Usage: /{cmd} `<id>`",
        "morning_greeting": "🌅 Good morning, {name}!\n\nWhat are your plans for today? Don't forget to check your tasks!\n\n/list — view tasks\n/add — add a new one",
        "help_title": (
            "📖 *Bot Help*\n\n"
            "➕ *Adding tasks*\n"
            "/add — add a new task (text, deadline, priority, category, repeat)\n\n"
            "📋 *Viewing tasks*\n"
            "/list — active tasks\n"
            "/list done — completed\n"
            "/list overdue — overdue\n"
            "/list all — all tasks\n"
            "/list high — high priority 🔴\n"
            "/list medium — medium priority 🟡\n"
            "/list low — low priority 🟢\n\n"
            "✅ *Managing tasks*\n"
            "/done `<id>` — mark as done\n"
            "/delete `<id>` — delete task\n\n"
            "⏰ *Reminders*\n"
            "/remind — tasks with deadlines\n"
            "Bot reminds automatically 1 hour before deadline\n\n"
            "🤖 *AI Assistant*\n"
            "/ai — launch AI assistant\n"
            "AI analyzes your tasks and gives advice.\n"
            "Just write:\n"
            "/aiend — end conversation with AI\n\n"
            "📊 *Other*\n"
            "/stats — completion statistics\n"
            "/lang — change language\n"
            "/help — this help\n\n"
            "💡 *Tip:* After /add the bot will guide you step by step!"
        ),
    }
}

def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["uk"]).get(key, key)
    return text.format(**kwargs) if kwargs else text