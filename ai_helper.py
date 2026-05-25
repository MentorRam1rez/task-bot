import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"

TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task for the user / Додати нову задачу користувачу",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Task text / Текст задачі"
                },
                "deadline": {
                    "type": "string",
                    "description": "Deadline in format DD.MM.YYYY HH:MM, or null if none"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Task priority"
                },
                "category": {
                    "type": "string",
                    "enum": ["work", "study", "personal"],
                    "description": "Task category"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task by ID / Видалити задачу за ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to delete"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "mark_task_done",
        "description": "Mark a task as completed / Позначити задачу як виконану",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to mark as done"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "get_tasks",
        "description": "Get user task list / Отримати список задач",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "done", "overdue", "all"],
                    "description": "Filter by status"
                }
            },
            "required": []
        }
    }
]


def _ask(prompt: str) -> str:
    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def classify_task(text: str) -> dict:
    prompt = f"""Ти помічник з тайм-менеджменту. Проаналізуй задачу і визнач її категорію та пріоритет.

Задача: "{text}"

Категорії: work (робота), study (навчання), personal (особисте)
Пріоритети: high (термінове/важливе), medium (звичайне), low (не термінове)

Відповідай ТІЛЬКИ у форматі JSON без пояснень:
{{"category": "work", "priority": "high"}}"""

    try:
        response = _ask(prompt)
        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])
        category = data.get("category", "personal")
        priority = data.get("priority", "medium")
        if category not in ("work", "study", "personal"):
            category = "personal"
        if priority not in ("high", "medium", "low"):
            priority = "medium"
        return {"category": category, "priority": priority}
    except Exception:
        return {"category": "personal", "priority": "medium"}


def morning_ai_message(name: str, tasks: list) -> str:
    if not tasks:
        prompt = f"""Ти дружній AI-помічник у Telegram-боті для задач.
Напиши коротке ранкове привітання для {name} — сьогодні у нього немає задач.
Порадь додати задачі на день. Максимум 3 речення. Без зайвих емодзі. Живою українською мовою."""
    else:
        task_list = "\n".join([
            f"- {t.text} (пріоритет: {t.priority}, дедлайн: {t.deadline.strftime('%H:%M') if t.deadline else 'немає'})"
            for t in tasks
        ])
        prompt = f"""Ти дружній AI-помічник у Telegram-боті для задач.
Напиши коротке ранкове привітання для {name}.

Задачі на сьогодні:
{task_list}

Порадь з чого почати день виходячи з пріоритетів. Максимум 4 речення. Живою українською мовою. Додай 1-2 емодзі."""

    try:
        return _ask(prompt)
    except Exception:
        return f"🌅 Доброго ранку, {name}! Гарного та продуктивного дня!"


def daytime_reminder_message(name: str, tasks: list) -> str:
    task_list = "\n".join([
        f"- {t.text} о {t.deadline.strftime('%H:%M')}"
        for t in tasks if t.deadline
    ])
    prompt = f"""Ти дружній AI-помічник у Telegram-боті для задач.
Напиши коротке живе нагадування для {name} про задачі на найближчі години.

Задачі:
{task_list}

Вимоги:
- Коротко, максимум 2-3 речення
- Жива розмовна українська, як від друга
- Кожного разу інша фраза — не шаблонна
- 1-2 емодзі"""

    try:
        return _ask(prompt)
    except Exception:
        return f"👋 {name}, не забудь про задачі на найближчі години!"


def evening_analysis_message(name: str, done: int, active: int, overdue: int) -> str:
    total = done + active + overdue
    prompt = f"""Ти дружній AI-помічник у Telegram-боті для задач.
Зроби вечірній аналіз дня для {name}.

Статистика за день:
- Виконано задач: {done}
- Залишилось активних: {active}
- Прострочено: {overdue}
- Всього: {total}

Вимоги:
- Живою розмовною українською, як від друга
- Якщо виконав багато — похвали щиро
- Якщо мало — підбадьори, не критикуй
- Якщо є прострочені — м'яко зазнач
- Дай коротку пораду або побажай відпочинку
- Максимум 4 речення
- 1-2 емодзі"""

    try:
        return _ask(prompt)
    except Exception:
        return f"🌙 {name}, день закінчується! Виконано {done} задач — молодець!"


def ai_analyze_tasks(tasks: list, name: str) -> str:
    if not tasks:
        prompt = f"""Ти дружній AI-помічник. Користувач {name} викликав тебе але у нього немає задач.
Привітайся, скажи що можеш керувати задачами — додавати, видаляти, позначати виконаними просто в чаті.
Максимум 2 речення. Жива українська."""
    else:
        active = [t for t in tasks if t.status == "active"]
        overdue = [t for t in tasks if t.status == "overdue"]

        task_list = "\n".join([
            f"- #{t.id} {t.text} (пріоритет: {t.priority}, дедлайн: {t.deadline.strftime('%d.%m %H:%M') if t.deadline else 'немає'})"
            for t in active[:5]
        ])
        overdue_list = "\n".join([
            f"- #{t.id} {t.text}" for t in overdue
        ]) if overdue else "немає"

        prompt = f"""Ти дружній AI-помічник з тайм-менеджменту.
Зроби короткий аналіз задач для {name} і дай головну пораду.

Активні задачі:
{task_list}

Прострочені:
{overdue_list}

Вимоги:
- Максимум 4 речення
- Скажи що найважливіше зробити зараз
- Якщо є прострочені — м'яко зазнач
- Жива українська, як від друга
- Скажи що можна просто написати щоб додати/видалити/виконати задачу"""

    try:
        return _ask(prompt)
    except Exception:
        return f"Привіт, {name}! Давай подивимось на твої задачі. Можу додавати, видаляти і позначати виконаними — просто напиши! 😊"


def ai_chat_with_tools(user_message: str, history: list, tasks: list, name: str) -> dict:
    if tasks:
        active = [t for t in tasks if t.status == "active"]
        overdue = [t for t in tasks if t.status == "overdue"]

        tasks_context = "User tasks / Задачі користувача:\n"
        if active:
            tasks_context += "\nActive / Активні:\n" + "\n".join([
                f"- #{t.id} {t.text} (priority: {t.priority}, deadline: {t.deadline.strftime('%d.%m %H:%M') if t.deadline else 'none'})"
                for t in active
            ])
        if overdue:
            tasks_context += "\n\nOverdue / Прострочені:\n" + "\n".join([
                f"- #{t.id} {t.text}" for t in overdue
            ])
    else:
        tasks_context = "No tasks yet / Задач поки немає."

    system_prompt = f"""You are a friendly AI assistant for task management in a Telegram bot.
Your name is Assistant. You are talking to {name}.

{tasks_context}

IMPORTANT LANGUAGE RULE:
- If the user writes in Ukrainian — respond in Ukrainian
- If the user writes in English — respond in English
- Always detect the language of the user's message and respond in the same language

You can:
- Give advice about tasks / Давати поради щодо задач
- Add new tasks using add_task tool
- Delete tasks using delete_task tool
- Mark tasks as done using mark_task_done tool
- Show task list using get_tasks tool

If the user asks to add/delete/complete a task — use the appropriate tool.
Communication style: friendly, casual, like a friend, brief (max 4-5 sentences)."""

    messages = history + [{"role": "user", "content": user_message}]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        for block in response.content:
            if block.type == "tool_use":
                text_before = ""
                for b in response.content:
                    if b.type == "text":
                        text_before = b.text
                        break
                return {
                    "type": "tool",
                    "tool": block.name,
                    "input": block.input,
                    "text": text_before,
                    "tool_use_id": block.id,
                }

        text = ""
        for block in response.content:
            if block.type == "text":
                text = block.text
                break
        return {"type": "text", "text": text}

    except Exception as e:
        print(f"AI chat error: {e}")
        return {"type": "text", "text": "Вибач, щось пішло не так. Спробуй ще раз 🙏"}