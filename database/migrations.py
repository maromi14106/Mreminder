from database.database import Database


class Migration:

    def __init__(self, db: Database) -> None:
        self._db = db

    def run(self) -> None:
        self.create_tasks_table()

    def create_tasks_table(self) -> None:
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            repeat_type TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
        self._db.execute(sql)
        self._db.commit()
