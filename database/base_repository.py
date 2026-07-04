import sqlite3
from collections.abc import Iterable, Sequence
from typing import Any

from database.database import Database


class BaseRepository:

    def __init__(self, db: Database) -> None:
        self._db = db

    def execute(
        self, sql: str, parameters: Sequence[Any] | None = None
    ) -> sqlite3.Cursor:
        if parameters is None:
            parameters = ()
        return self._db.execute(sql, parameters)

    def executemany(
        self, sql: str, seq_of_parameters: Iterable[Sequence[Any]]
    ) -> sqlite3.Cursor:
        return self._db.executemany(sql, seq_of_parameters)

    def commit(self) -> None:
        self._db.commit()
