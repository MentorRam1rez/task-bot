import os
import anthropic
from typing import Optional

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _ask(prompt: str) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def classify_task(text: str) -> dict:
    """Визначає категорію і пріоритет задачі."""
    prompt = f"""Ти помічник з тайм-менеджменту. Проаналізуй задачу і визнач її категорію та пріоритет.

Задача: "{text}"

Категорії: work (робота), study (навчання), personal (особисте)
Пріоритети: high (термінове/важливе), medium (звичайне), low (не термінове)

Відповідай ТІЛЬКИ у форматі JSON без пояснень:
{{"category": "work", "priority": "high"}}"""

    try:
        response = _ask(prompt)
        import json
        # Витягуємо JSON з відповіді
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
    """Генерує персоналізоване ранкове повідомлення."""
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
    """Генерує денне нагадування про найближчі задачі."""
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
    """Генерує вечірній аналіз дня."""
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