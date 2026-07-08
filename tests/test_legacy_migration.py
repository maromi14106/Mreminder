import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from database.legacy_migration import (
    migrate_legacy_database,
    LegacyDatabaseMigrationError,
)


def setup_db_with_table(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)")
    conn.execute("INSERT INTO test_table (value) VALUES ('test_data')")
    conn.commit()
    conn.close()


def test_migrate_legacy_database_success(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"

    setup_db_with_table(source_db)

    # Destination should not exist
    assert not dest_db.exists()

    result = migrate_legacy_database(source_db, dest_db)

    assert result is True
    assert dest_db.exists()
    assert source_db.exists()  # Source should not be deleted

    # Check if data was copied
    conn = sqlite3.connect(dest_db)
    cursor = conn.execute("SELECT value FROM test_table")
    row = cursor.fetchone()
    conn.close()

    assert row[0] == "test_data"

    # Check that no tmp db is left
    assert len(list(dest_db.parent.glob("*.tmp.db"))) == 0


def test_migrate_legacy_database_dest_exists(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"

    setup_db_with_table(source_db)
    setup_db_with_table(dest_db)

    # Overwrite value to verify it's not changed
    conn = sqlite3.connect(dest_db)
    conn.execute("UPDATE test_table SET value = 'dest_data'")
    conn.commit()
    conn.close()

    result = migrate_legacy_database(source_db, dest_db)

    assert result is False  # Should not migrate if dest exists

    # Verify dest content is maintained
    conn = sqlite3.connect(dest_db)
    cursor = conn.execute("SELECT value FROM test_table")
    assert cursor.fetchone()[0] == "dest_data"
    conn.close()


def test_migrate_legacy_database_source_not_exists(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"

    result = migrate_legacy_database(source_db, dest_db)

    assert result is False
    assert not dest_db.exists()


def test_migrate_legacy_database_same_path(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    setup_db_with_table(source_db)

    result = migrate_legacy_database(source_db, source_db)

    assert result is False


def test_migrate_legacy_database_quick_check_none(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"
    setup_db_with_table(source_db)

    with patch("database.legacy_migration.sqlite3.connect") as mock_connect:
        mock_source = MagicMock()
        mock_tmp = MagicMock()

        # Second connect returns tmp, first returns source
        mock_connect.side_effect = [mock_source, mock_tmp]

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_tmp.execute.return_value = mock_cursor

        with pytest.raises(
            LegacyDatabaseMigrationError, match="Database integrity check failed"
        ):
            migrate_legacy_database(source_db, dest_db)

        assert not dest_db.exists()
        assert len(list(dest_db.parent.glob("*.tmp.db"))) == 0


def test_migrate_legacy_database_quick_check_fail(tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"
    setup_db_with_table(source_db)

    with patch("database.legacy_migration.sqlite3.connect") as mock_connect:
        mock_source = MagicMock()
        mock_tmp = MagicMock()

        # Second connect returns tmp, first returns source
        mock_connect.side_effect = [mock_source, mock_tmp]

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ["malformed"]
        mock_tmp.execute.return_value = mock_cursor

        with pytest.raises(
            LegacyDatabaseMigrationError, match="Database integrity check failed"
        ):
            migrate_legacy_database(source_db, dest_db)

        assert not dest_db.exists()
        assert len(list(dest_db.parent.glob("*.tmp.db"))) == 0


@patch("pathlib.Path.replace")
def test_migrate_legacy_database_replace_fails(mock_replace, tmp_path):
    source_db = tmp_path / "source" / "legacy.db"
    dest_db = tmp_path / "dest" / "new.db"
    setup_db_with_table(source_db)

    mock_replace.side_effect = OSError("Access Denied")

    with pytest.raises(
        LegacyDatabaseMigrationError, match="Failed to move database file"
    ):
        migrate_legacy_database(source_db, dest_db)

    assert not dest_db.exists()
    assert len(list(dest_db.parent.glob("*.tmp.db"))) == 0
