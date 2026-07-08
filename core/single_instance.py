"""Single instance application module."""

import hashlib
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QLockFile
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from core.app_paths import get_app_data_dir


class SingleInstanceError(Exception):
    """Exception raised for errors in the single instance module."""

    pass


class SingleInstance(QObject):
    """Class to ensure only a single instance of the application is running."""

    show_requested = Signal()

    def __init__(
        self, lock_path: Path | None = None, server_name: str | None = None
    ) -> None:
        """Initialize the SingleInstance."""
        super().__init__()

        if lock_path and server_name:
            self._lock_path = lock_path
            self._server_name = server_name
        else:
            app_data_dir = get_app_data_dir()
            self._lock_path = (
                lock_path if lock_path else app_data_dir / "mreminder.lock"
            )

            if server_name:
                self._server_name = server_name
            else:
                # Create a stable hash based on the app data directory
                dir_hash = hashlib.sha256(
                    str(app_data_dir).encode("utf-8")
                ).hexdigest()[:16]
                self._server_name = f"mreminder_ipc_{dir_hash}"

        self._is_primary = False
        self._server: QLocalServer | None = None
        self._lock_file: QLockFile | None = None

        self._check_and_start()

    @property
    def is_primary(self) -> bool:
        """Return True if this is the primary instance."""
        return self._is_primary

    def _check_and_start(self) -> None:
        """Check if another instance is running, otherwise start the local server."""
        self._lock_file = QLockFile(str(self._lock_path))
        self._lock_file.setStaleLockTime(0)

        if self._lock_file.tryLock(0):
            # We got the lock, we are the primary instance
            self._is_primary = True

            self._server = QLocalServer()
            self._server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)

            if not self._server.listen(self._server_name):
                # Try to remove stale server socket if it exists and try again
                QLocalServer.removeServer(self._server_name)
                if not self._server.listen(self._server_name):
                    self._lock_file.unlock()
                    error_msg = self._server.errorString()
                    raise SingleInstanceError(
                        f"Failed to listen on QLocalServer: {error_msg}"
                    )

            self._server.newConnection.connect(self._handle_new_connection)
        else:
            # We failed to get the lock, we are a secondary instance
            self._is_primary = False

    def notify_primary(self, silent: bool = False) -> None:
        """Send a message to the primary instance.

        Retries connection for up to 2 seconds.
        Raises SingleInstanceError on failure.
        """
        if self.is_primary:
            return

        message = "PING" if silent else "SHOW"
        max_retries = 10
        retry_interval_ms = 200

        for attempt in range(1, max_retries + 1):
            socket = QLocalSocket()
            socket.connectToServer(self._server_name)

            if socket.waitForConnected(retry_interval_ms):
                bytes_written = socket.write(message.encode("utf-8"))
                if bytes_written < 0:
                    error_msg = socket.errorString()
                    raise SingleInstanceError(
                        f"Failed to write to primary instance (Server: {self._server_name}, Message: '{message}', Attempt: {attempt}): {error_msg}"
                    )
                socket.flush()

                if not socket.waitForBytesWritten(500):
                    if socket.bytesToWrite() > 0:
                        error_msg = socket.errorString()
                        raise SingleInstanceError(
                            f"Failed to write to primary instance (Server: {self._server_name}, Message: '{message}', Attempt: {attempt}): waitForBytesWritten failed and bytesToWrite > 0: {error_msg}"
                        )

                socket.disconnectFromServer()
                socket.waitForDisconnected(500)
                return

            # Connection failed, wait and retry
            time.sleep(retry_interval_ms / 1000.0)

        # Total timeout
        raise SingleInstanceError(
            f"Failed to connect to primary instance after {max_retries} attempts (Server: {self._server_name}, Message: '{message}')"
        )

    def _handle_new_connection(self) -> None:
        """Handle incoming connections from secondary instances."""
        if self._server is None:
            return

        socket = self._server.nextPendingConnection()
        if not socket:
            return

        if socket.waitForReadyRead(500):
            message = socket.readAll().data().decode("utf-8")
            if message == "SHOW":
                self.show_requested.emit()
            elif message == "PING":
                pass  # Just existence check
            else:
                pass  # Ignore unknown messages

        socket.disconnectFromServer()
        socket.deleteLater()

    def close(self) -> None:
        """Close the local server and release the lock."""
        if self._is_primary:
            if self._server:
                if self._server.isListening():
                    self._server.close()
                # Do not unconditionally call removeServer, only cleanup what we own
                QLocalServer.removeServer(self._server_name)
                self._server = None

            if self._lock_file:
                if self._lock_file.isLocked():
                    self._lock_file.unlock()
                self._lock_file = None

            self._is_primary = False
