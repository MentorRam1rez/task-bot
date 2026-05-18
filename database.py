import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    user_id: int
    text: str
    deadline: Optional[datetime]
    status: str
    created_at: datetime
    priority: str = "medium"
    category: Optional[str] = None
    repeat_type: Optional[str] = None
    repeat_days: Optional[str] = None

class Database:
    def __init__(self):
        url = os.getenv("DATABASE_URL", "")
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        self.conn = psycopg2.connect(url, sslmode="require")
        self.conn.autocommit = True
        self._create_tables()

    def _create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id          SERIAL PRIMARY KEY,
                    user_id     BIGINT    NOT NULL,
                    text        TEXT      NOT NULL,
                    deadline    TIMESTAMP DEFAULT NULL,
                    status      TEXT      NOT NULL DEFAULT 'active',
                    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
                    priority    TEXT      NOT NULL DEFAULT 'medium',
                    category    TEXT      DEFAULT NULL,
                    repeat_type TEXT      DEFAULT NULL,
                    repeat_days TEXT      DEFAULT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);

                CREATE TABLE IF NOT EXISTS reminder_log (
                    task_id INTEGER NOT NULL PRIMARY KEY,
                    sent_at TIMESTAMP NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id  BIGINT PRIMARY KEY,
                    language TEXT NOT NULL DEFAULT 'uk'
                );

                ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority TEXT NOT NULL DEFAULT 'medium';
                ALTER TABLE tasks ADD COLUMN IF NOT EXISTS category TEXT DEFAULT NULL;
                ALTER TABLE tasks ADD COLUMN IF NOT EXISTS repeat_type TEXT DEFAULT NULL;
                ALTER TABLE tasks ADD COLUMN IF NOT EXISTS repeat_days TEXT DEFAULT NULL;
            """)

    def _row_to_task(self, row) -> Task:
        return Task(
            id=row[0],
            user_id=row[1],
            text=row[2],
            deadline=row[3],
            status=row[4],
            created_at=row[5],
            priority=row[6] if len(row) > 6 else "medium",
            category=row[7] if len(row) > 7 else None,
            repeat_type=row[8] if len(row) > 8 else None,
            repeat_days=row[9] if len(row) > 9 else None,
        )

    def get_language(self, user_id: int) -> str:
        with self.conn.cursor() as cur:
            cur.execute("SELECT language FROM user_settings WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else "uk"

    def set_language(self, user_id: int, lang: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_settings (user_id, language) VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET language = EXCLUDED.language
            """, (user_id, lang))

    def add_task(self, user_id: int, text: str, deadline: Optional[datetime] = None,
                 priority: str = "medium", category: Optional[str] = None,
                 repeat_type: Optional[str] = None, repeat_days: Optional[str] = None) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO tasks (user_id, text, deadline, priority, category, repeat_type, repeat_days)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (user_id, text, deadline, priority, category, repeat_type, repeat_days),
            )
            return cur.fetchone()[0]

    def get_tasks(self, user_id: int, status: str = "active",
                  category: Optional[str] = None) -> List[Task]:
        with self.conn.cursor() as cur:
            if status == "all":
                if category:
                    cur.execute(
                        "SELECT * FROM tasks WHERE user_id=%s AND category=%s ORDER BY priority DESC, deadline NULLS LAST",
                        (user_id, category),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM tasks WHERE user_id=%s ORDER BY priority DESC, deadline NULLS LAST",
                        (user_id,),
                    )
            else:
                if category:
                    cur.execute(
                        "SELECT * FROM tasks WHERE user_id=%s AND status=%s AND category=%s ORDER BY priority DESC, deadline NULLS LAST",
                        (user_id, status, category),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM tasks WHERE user_id=%s AND status=%s ORDER BY priority DESC, deadline NULLS LAST",
                        (user_id, status),
                    )
            return [self._row_to_task(r) for r in cur.fetchall()]

    def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (task_id, user_id))
            row = cur.fetchone()
            return self._row_to_task(row) if row else None

    def mark_done(self, user_id: int, task_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status='done' WHERE id=%s AND user_id=%s AND status='active'",
                (task_id, user_id),
            )
            return cur.rowcount > 0

    def delete_task(self, user_id: int, task_id: int) -> bool:
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, user_id))
            return cur.rowcount > 0

    def get_stats(self, user_id: int) -> dict:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE status='done') as done,
                    COUNT(*) FILTER (WHERE status='active') as active,
                    COUNT(*) FILTER (WHERE status='overdue') as overdue,
                    COUNT(*) as total
                FROM tasks WHERE user_id=%s
            """, (user_id,))
            row = cur.fetchone()
            done, active, overdue, total = row
            percent = round((done / total * 100) if total > 0 else 0)
            return {"done": done, "active": active, "overdue": overdue, "total": total, "percent": percent}

    def get_upcoming_tasks(self, from_dt: datetime, to_dt: datetime) -> List[Task]:
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT t.* FROM tasks t
                   LEFT JOIN reminder_log r ON r.task_id = t.id
                   WHERE t.status = 'active'
                     AND t.deadline BETWEEN %s AND %s
                     AND r.task_id IS NULL""",
                (from_dt, to_dt),
            )
            return [self._row_to_task(r) for r in cur.fetchall()]

    def get_repeating_tasks(self) -> List[Task]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM tasks WHERE status='done' AND repeat_type IS NOT NULL"
            )
            return [self._row_to_task(r) for r in cur.fetchall()]

    def reset_repeating_task(self, task_id: int, new_deadline: datetime):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status='active', deadline=%s WHERE id=%s",
                (new_deadline, task_id),
            )

    def log_reminder(self, task_id: int):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reminder_log (task_id) VALUES (%s) ON CONFLICT DO NOTHING",
                (task_id,),
            )

    def mark_overdue(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET status='overdue' WHERE status='active' AND deadline < NOW()"
            )

    def get_all_users(self) -> List[int]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM tasks")
            return [row[0] for row in cur.fetchall()]

    def get_tasks_by_priority(self, user_id: int, priority: str) -> List[Task]:
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM tasks WHERE user_id=%s AND priority=%s AND status='active'
                   ORDER BY deadline NULLS LAST""",
                (user_id, priority),
            )
            return [self._row_to_task(r) for r in cur.fetchall()]