import sqlite3
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
    def __init__(self, db_path: str = "tasks.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER  NOT NULL,
                text       TEXT     NOT NULL,
                deadline   DATETIME DEFAULT NULL,
                status     TEXT     NOT NULL DEFAULT 'active',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, deadline);

            CREATE TABLE IF NOT EXISTS reminder_log (
                task_id INTEGER NOT NULL PRIMARY KEY,
                sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def _row_to_task(self, row) -> Task:
        deadline = None
        if row["deadline"]:
            try:
                deadline = datetime.fromisoformat(row["deadline"])
            except ValueError:
                pass
        return Task(
            id=row["id"],
            user_id=row["user_id"],
            text=row["text"],
            deadline=deadline,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def add_task(self, user_id: int, text: str, deadline: Optional[datetime] = None) -> int:
        dl_str = deadline.isoformat() if deadline else None
        cursor = self.conn.execute(
            "INSERT INTO tasks (user_id, text, deadline) VALUES (?, ?, ?)",
            (user_id, text, dl_str),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks(self, user_id: int, status: str = "active") -> List[Task]:
        if status == "all":
            rows = self.conn.execute(
                "SELECT * FROM tasks WHERE user_id=? ORDER BY deadline NULLS LAST, id",
                (user_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM tasks WHERE user_id=? AND status=? ORDER BY deadline NULLS LAST, id",
                (user_id, status),
            ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def get_task(self, user_id: int, task_id: int) -> Optional[Task]:
        row = self.conn.execute(
            "SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, user_id)
        ).fetchone()
        return self._row_to_task(row) if row else None

    def mark_done(self, user_id: int, task_id: int) -> bool:
        cursor = self.conn.execute(
            "UPDATE tasks SET status='done' WHERE id=? AND user_id=? AND status='active'",
            (task_id, user_id),
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, user_id: int, task_id: int) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_upcoming_tasks(self, from_dt: datetime, to_dt: datetime) -> List[Task]:
        rows = self.conn.execute(
            """SELECT t.* FROM tasks t
               LEFT JOIN reminder_log r ON r.task_id = t.id
               WHERE t.status = 'active'
                 AND t.deadline BETWEEN ? AND ?
                 AND r.task_id IS NULL""",
            (from_dt.isoformat(), to_dt.isoformat()),
        ).fetchall()
        return [self._row_to_task(r) for r in rows]

    def log_reminder(self, task_id: int):
        self.conn.execute(
            "INSERT OR IGNORE INTO reminder_log (task_id) VALUES (?)", (task_id,)
        )
        self.conn.commit()

    def mark_overdue(self):
        now = datetime.now().isoformat()
        self.conn.execute(
            "UPDATE tasks SET status='overdue' WHERE status='active' AND deadline < ?",
            (now,),
        )
        self.conn.commit()