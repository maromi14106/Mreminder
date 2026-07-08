from database.database import Database


def test_database_initialization_with_path(tmp_path):
    """Test that Database can be initialized with a specific path."""
    db_path = tmp_path / "test.db"

    # Path shouldn't exist initially
    assert not db_path.exists()

    db = Database(db_path=db_path)

    # Initialization should create the path
    assert db_path.exists()

    # Can execute simple query
    cursor = db.execute("PRAGMA journal_mode;")
    assert cursor.fetchone() is not None
    db.close()


def test_database_context_manager(tmp_path):
    """Test that Database works as a context manager."""
    db_path = tmp_path / "test2.db"

    with Database(db_path=db_path) as db:
        cursor = db.execute("PRAGMA foreign_keys;")
        assert cursor.fetchone() is not None
