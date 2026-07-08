"""Windows autostart registry module."""

import winreg


class AutoStartError(Exception):
    """Exception raised for errors in the autostart registry operations."""

    pass


class AutoStartRegistry:
    """Class to manage Windows autostart registry."""

    VALUE_NAME = "Mreminder"
    REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def get_command(self) -> str | None:
        """Get the current autostart command from the registry."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH, 0, winreg.KEY_READ
            ) as key:
                value, _ = winreg.QueryValueEx(key, self.VALUE_NAME)
                return str(value)
        except FileNotFoundError:
            return None
        except OSError as e:
            raise AutoStartError(f"Failed to read autostart registry: {e}") from e

    def set_command(self, command: str) -> None:
        """Set the autostart command in the registry."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH, 0, winreg.KEY_WRITE
            ) as key:
                winreg.SetValueEx(key, self.VALUE_NAME, 0, winreg.REG_SZ, command)
        except OSError as e:
            raise AutoStartError(f"Failed to write autostart registry: {e}") from e

    def remove(self) -> None:
        """Remove the autostart command from the registry."""
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH, 0, winreg.KEY_WRITE
            ) as key:
                try:
                    winreg.DeleteValue(key, self.VALUE_NAME)
                except FileNotFoundError:
                    # 値が存在しない場合は正常終了とする
                    pass
        except OSError as e:
            raise AutoStartError(f"Failed to delete autostart registry: {e}") from e
