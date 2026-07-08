"""Legacy database migration module."""

import os
import sqlite3
import tempfile
from pathlib import Path


class LegacyDatabaseMigrationError(Exception):
    """Exception raised for errors during legacy database migration."""

    pass


def migrate_legacy_database(source_path: Path, destination_path: Path) -> bool:
    """Migrate the legacy database to the new location.

    Returns:
        bool: True if migration occurred, False otherwise (e.g. source does not exist,
              destination already exists, or paths are identical).

    Raises:
        LegacyDatabaseMigrationError: If migration fails.
    """
    try:
        source_real = source_path.resolve()
        dest_real = destination_path.resolve()

        if source_real == dest_real:
            return False
    except OSError:
        pass

    if not source_path.exists() or destination_path.exists():
        return False

    destination_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary file in the same directory as destination
    fd, tmp_path_str = tempfile.mkstemp(suffix=".tmp.db", dir=destination_path.parent)
    os.close(fd)
    tmp_path = Path(tmp_path_str)

    source_conn = None
    tmp_conn = None
    migration_success = False

    try:
        source_conn = sqlite3.connect(
            source_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        tmp_conn = sqlite3.connect(
            tmp_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )

        # Backup the database
        source_conn.backup(tmp_conn)

        # Verify backup integrity
        cursor = tmp_conn.execute("PRAGMA quick_check;")
        result = cursor.fetchone()

        if result is None or result[0] != "ok":
            raise LegacyDatabaseMigrationError(
                f"Database integrity check failed after backup: {result[0] if result else 'None'}"
            )

        migration_success = True

    except sqlite3.Error as e:
        raise LegacyDatabaseMigrationError(f"Failed to migrate database: {e}") from e
    finally:
        if source_conn:
            source_conn.close()
        if tmp_conn:
            tmp_conn.close()

        # Clean up tmp_path if migration failed before os.replace
        if not migration_success and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    if migration_success:
        try:
            # Atomic replace
            tmp_path.replace(destination_path)
        except OSError as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            raise LegacyDatabaseMigrationError(
                f"Failed to move database file: {e}"
            ) from e

    return True
