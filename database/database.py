import sqlite3
from pathlib import Path
from typing import Any
from collections.abc import Iterable, Sequence
from types import TracebackType

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "kokumaro.db"


class Database:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        # DBを保存するディレクトリが存在しない場合は作成
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )

        self._connection.execute("PRAGMA foreign_keys = ON;")
        self._connection.execute("PRAGMA journal_mode = WAL;")

        self._connection.row_factory = sqlite3.Row

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def execute(
        self, sql: str, parameters: Sequence[Any] = ()
    ) -> sqlite3.Cursor:
        return self._connection.execute(sql, parameters)

    def executemany(
        self, sql: str, seq_of_parameters: Iterable[Sequence[Any]]
    ) -> sqlite3.Cursor:
        return self._connection.executemany(sql, seq_of_parameters)

    def commit(self) -> None:
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
