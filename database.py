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

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
        self.conn.autocommit = True
        self._create_tables()

    def _create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id         SERIAL PRIMARY KEY,
                    user_id    BIGINT   NOT NULL,
                    text       TEXT     NOT NULL,
                    deadline   TIMESTAMP DEFAULT NULL,
                    status     TEXT     NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);

                CREATE TABLE IF NOT EXISTS reminder_log (
                    task_id INTEGER NOT NULL PRIMARY KEY,
                    sent_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)

    def _row_to_task(self, row) -> Task:
        return Task(
            id=row[0],
            user_id=row[1],
            text=row[2],
            deadline=row[3],
            status=row[4],
            created_at=row[5],
        )

    def add_task(self, user_id: int, text: str, deadline: Optional[datetime] = None) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (user_id, text, deadline) VALUES (%s, %s, %s) RETURNING id",
                (user_id, text, deadline),
            )
            return cur.fetchone()[0]

    def get_tasks(self, user_id: int, status: str = "active") -> List[Task]:
        with self.conn.cursor() as cur:
            if status == "all":
                cur.execute(
                    "SELECT * FROM tasks WHERE user_id=%s ORDER BY deadline NULLS LAST, id",
                    (user_id,),
                )
            else:
                cur.execute(
                    "SELECT * FROM tasks WHERE user_id=%s AND status=%s ORDER BY deadline NULLS LAST, id",
                    (user_id, status),
                )
            return [self._row_to_task(r) for r in cur.fetchall()]

    def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM tasks WHERE id=%s AND user_id=%s",
                (task_id, user_id),
            )
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
            cur.execute(
                "DELETE FROM tasks WHERE id=%s AND user_id=%s",
                (task_id, user_id),
            )
            return cur.rowcount > 0

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