import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from core.single_instance import SingleInstance, SingleInstanceError


@pytest.fixture
def mock_server_and_socket_and_lock():
    with patch("core.single_instance.QLocalServer") as mock_server_cls, patch(
        "core.single_instance.QLocalSocket"
    ) as mock_socket_cls, patch(
        "core.single_instance.QLockFile"
    ) as mock_lock_cls, patch(
        "core.single_instance.get_app_data_dir"
    ) as mock_get_app_data_dir:

        mock_get_app_data_dir.return_value = MagicMock()

        # Setup mock socket
        mock_socket = MagicMock()
        mock_socket_cls.return_value = mock_socket

        # Setup mock server
        mock_server = MagicMock()
        mock_server_cls.return_value = mock_server

        # Setup mock lock
        mock_lock = MagicMock()
        mock_lock_cls.return_value = mock_lock

        # Mock removeServer
        mock_server_cls.removeServer = MagicMock()

        yield mock_server_cls, mock_socket_cls, mock_lock_cls, mock_server, mock_socket, mock_lock


def test_single_instance_first_launch(mock_server_and_socket_and_lock):
    """Test that the first instance is recognized as primary when QLockFile succeeds."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = True
    mock_server.listen.return_value = True

    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    assert instance.is_primary is True
    mock_lock.tryLock.assert_called_once_with(0)
    mock_server.listen.assert_called_with("test_server")
    mock_server.newConnection.connect.assert_called_once()
    mock_server_cls.removeServer.assert_not_called()


def test_single_instance_second_launch(mock_server_and_socket_and_lock):
    """Test that the second instance is not primary when QLockFile fails."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False

    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    assert instance.is_primary is False
    mock_server.listen.assert_not_called()
    mock_server_cls.removeServer.assert_not_called()


def test_single_instance_listen_fails_removes_socket_and_unlocks(
    mock_server_and_socket_and_lock,
):
    """Test that if listen fails twice, lock is released and error raised."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = True
    mock_server.listen.side_effect = [False, False]

    with pytest.raises(SingleInstanceError):
        SingleInstance(server_name="test_server")

    mock_server_cls.removeServer.assert_called_once_with("test_server")
    mock_lock.unlock.assert_called_once()


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_success(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that notify_primary sends message successfully."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    # Connect succeeds on first try
    mock_socket.waitForConnected.return_value = True
    mock_socket.waitForBytesWritten.return_value = True
    mock_socket.write.return_value = 4

    instance.notify_primary(silent=False)

    mock_socket.write.assert_called_with(b"SHOW")
    mock_socket.flush.assert_called_once()
    mock_socket.waitForBytesWritten.assert_called_once()
    mock_socket.disconnectFromServer.assert_called_once()
    mock_sleep.assert_not_called()


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_retry_creates_new_socket(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that each retry creates a new QLocalSocket."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        _,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    mock_socket_1 = MagicMock()
    mock_socket_1.waitForConnected.return_value = False

    mock_socket_2 = MagicMock()
    mock_socket_2.waitForConnected.return_value = True
    mock_socket_2.write.return_value = 4
    mock_socket_2.waitForBytesWritten.return_value = True

    mock_socket_cls.side_effect = [mock_socket_1, mock_socket_2]

    instance.notify_primary(silent=False)

    assert mock_socket_cls.call_count == 2
    mock_socket_1.write.assert_not_called()
    mock_socket_2.write.assert_called_once_with(b"SHOW")
    mock_sleep.assert_called_once()


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_write_negative_raises(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that notify_primary raises error when write returns negative value."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    mock_socket.waitForConnected.return_value = True
    mock_socket.write.return_value = -1
    mock_socket.errorString.return_value = "Mock Write Error"

    with pytest.raises(
        SingleInstanceError,
        match="Failed to write to primary instance \\(Server: test_server, Message: 'SHOW', Attempt: 1\\): Mock Write Error",
    ):
        instance.notify_primary(silent=False)


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_wait_false_bytes_zero_success(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that notify_primary succeeds when waitForBytesWritten=False but bytesToWrite=0."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    mock_socket.waitForConnected.return_value = True
    mock_socket.waitForBytesWritten.return_value = False
    mock_socket.bytesToWrite.return_value = 0
    mock_socket.write.return_value = 4

    instance.notify_primary(silent=False)

    mock_socket.write.assert_called_with(b"SHOW")
    mock_socket.flush.assert_called_once()
    mock_socket.waitForBytesWritten.assert_called_once()
    mock_socket.bytesToWrite.assert_called_once()
    mock_socket.disconnectFromServer.assert_called_once()
    mock_sleep.assert_not_called()


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_wait_false_bytes_positive_raises(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that notify_primary raises error when waitForBytesWritten=False and bytesToWrite>0."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    mock_socket.waitForConnected.return_value = True
    mock_socket.waitForBytesWritten.return_value = False
    mock_socket.bytesToWrite.return_value = 4
    mock_socket.write.return_value = 4
    mock_socket.errorString.return_value = "Mock Wait Error"

    with pytest.raises(
        SingleInstanceError,
        match="Failed to write to primary instance \\(Server: test_server, Message: 'SHOW', Attempt: 1\\): waitForBytesWritten failed and bytesToWrite > 0: Mock Wait Error",
    ):
        instance.notify_primary(silent=False)


@patch("core.single_instance.time.sleep")
def test_single_instance_notify_primary_total_fail_raises(
    mock_sleep, mock_server_and_socket_and_lock
):
    """Test that complete connection failure raises SingleInstanceError."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False
    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    mock_socket.waitForConnected.return_value = False

    with pytest.raises(
        SingleInstanceError, match="Failed to connect to primary instance"
    ):
        instance.notify_primary(silent=False)

    assert mock_socket.waitForConnected.call_count == 10
    assert mock_sleep.call_count == 10


def test_single_instance_close_double_call(mock_server_and_socket_and_lock):
    """Test that calling close twice is safe."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = True
    mock_server.listen.return_value = True
    mock_lock.isLocked.return_value = True

    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    instance.close()
    mock_server.close.assert_called_once()
    mock_server_cls.removeServer.assert_called_once_with("test_server")
    mock_lock.unlock.assert_called_once()

    # Second call
    instance.close()
    assert mock_server.close.call_count == 1
    assert mock_lock.unlock.call_count == 1


def test_single_instance_secondary_does_not_close_server(
    mock_server_and_socket_and_lock,
):
    """Test that secondary instance does not unlock or remove server on close."""
    (
        mock_server_cls,
        mock_socket_cls,
        mock_lock_cls,
        mock_server,
        mock_socket,
        mock_lock,
    ) = mock_server_and_socket_and_lock

    mock_lock.tryLock.return_value = False

    instance = SingleInstance(lock_path=Path("dummy.lock"), server_name="test_server")

    instance.close()
    mock_server.close.assert_not_called()
    mock_server_cls.removeServer.assert_not_called()
    mock_lock.unlock.assert_not_called()
