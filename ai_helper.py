import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _ask(prompt: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
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
        import json
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


def ai_chat(user_message: str, history: list, tasks: list, name: str) -> str:
    if tasks:
        active = [t for t in tasks if t.status == "active"]
        overdue = [t for t in tasks if t.status == "overdue"]
        done = [t for t in tasks if t.status == "done"]

        tasks_context = "Задачі користувача:\n"
        if active:
            tasks_context += "\nАктивні:\n" + "\n".join([
                f"- #{t.id} {t.text} (пріоритет: {t.priority}, дедлайн: {t.deadline.strftime('%d.%m %H:%M') if t.deadline else 'немає'})"
                for t in active
            ])
        if overdue:
            tasks_context += "\n\nПрострочені:\n" + "\n".join([
                f"- #{t.id} {t.text}" for t in overdue
            ])
        if done:
            tasks_context += f"\n\nВиконано: {len(done)} задач"
    else:
        tasks_context = "У користувача поки немає задач."

    system_prompt = f"""Ти дружній AI-помічник з тайм-менеджменту у Telegram-боті.
Тебе звати Асистент. Ти спілкуєшся з {name}.

{tasks_context}

Твої можливості:
- Давати поради щодо невиконаних задач
- Допомагати розставити пріоритети
- Мотивувати і підтримувати
- Відповідати на будь-які питання про продуктивність

Стиль спілкування:
- Жива розмовна українська мова
- Як друг, не як робот
- Коротко і по суті (максимум 4-5 речень)
- Якщо питають про конкретну задачу — давай конкретну пораду
- Можеш використовувати 1-2 емодзі"""

    messages = history + [{"role": "user", "content": user_message}]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"AI chat error: {e}")
        return "Вибач, щось пішло не так. Спробуй ще раз 🙏"


def ai_analyze_tasks(tasks: list, name: str) -> str:
    if not tasks:
        prompt = f"""Ти дружній AI-помічник. Користувач {name} викликав тебе але у нього немає задач.
Привітайся, скажи що можеш допомогти і запропонуй додати задачі через /add.
Максимум 2 речення. Жива українська."""
    else:
        active = [t for t in tasks if t.status == "active"]
        overdue = [t for t in tasks if t.status == "overdue"]

        task_list = "\n".join([
            f"- #{t.id} {t.text} (пріоритет: {t.priority}, дедлайн: {t.deadline.strftime('%d.%m %H:%M') if t.deadline else 'немає'})"
            for t in active[:5]
        ])
        overdue_list = "\n".join([f"- #{t.id} {t.text}" for t in overdue]) if overdue else "немає"

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
- Закінчи фразою що можна ставити питання"""

    try:
        return _ask(prompt)
    except Exception:
        return f"Привіт, {name}! Давай подивимось на твої задачі разом. Що тебе цікавить? 😊"