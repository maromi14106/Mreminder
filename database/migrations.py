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
            snoozed_until TEXT
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
            
        self._db.commit()
