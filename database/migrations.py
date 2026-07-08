from database.database import Database


class Migration:
    """Database migration runner."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def run(self) -> None:
        """Run all migrations."""
        self.create_tasks_table()
        self.add_notification_columns()

    def create_tasks_table(self) -> None:
        """Create the tasks table if it does not exist."""
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            repeat_type TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_notified_at TEXT,
            snoozed_until TEXT,
            next_run_at TEXT NOT NULL,
            weekday INTEGER
        );
        """
        self._db.execute(sql)
        self._db.commit()

    def add_notification_columns(self) -> None:
        """Add notification columns if they do not exist."""
        cursor = self._db.execute("PRAGMA table_info(tasks)")
        columns = [row["name"] for row in cursor.fetchall()]

        if "last_notified_at" not in columns:
            self._db.execute("ALTER TABLE tasks ADD COLUMN last_notified_at TEXT")
        if "snoozed_until" not in columns:
            self._db.execute("ALTER TABLE tasks ADD COLUMN snoozed_until TEXT")
        if "next_run_at" not in columns:
            self._db.execute("ALTER TABLE tasks ADD COLUMN next_run_at TEXT")
        if "weekday" not in columns:
            self._db.execute("ALTER TABLE tasks ADD COLUMN weekday INTEGER")

        self._db.commit()

        self._backfill_next_run_at()

    def _backfill_next_run_at(self) -> None:
        """Backfill next_run_at and weekday for existing records if missing."""
        cursor = self._db.execute(
            "SELECT id, remind_at, repeat_type FROM tasks WHERE next_run_at IS NULL OR next_run_at = ''"
        )
        rows = cursor.fetchall()

        if not rows:
            return

        from datetime import datetime
        from core.schedule import backfill_migration_next_run

        now = datetime.now()

        for row in rows:
            task_id = row["id"]
            remind_at = row["remind_at"]
            repeat_type = row["repeat_type"]

            next_run, weekday = backfill_migration_next_run(now, remind_at, repeat_type)

            self._db.execute(
                "UPDATE tasks SET next_run_at = ?, weekday = ? WHERE id = ?",
                (next_run, weekday, task_id),
            )

        self._db.commit()
