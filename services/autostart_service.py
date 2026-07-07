"""Autostart service module."""

import sys
from pathlib import Path

from core.autostart import AutoStartRegistry


class AutoStartService:
    """Service class for managing autostart settings."""

    def __init__(self, registry: AutoStartRegistry) -> None:
        """Initialize the AutoStartService."""
        self._registry = registry

    def get_launch_command(self) -> str:
        """Get the launch command for autostart, appending --silent."""
        if getattr(sys, "frozen", False):
            # PyInstaller exe
            exe_path = Path(sys.executable).resolve()
            return f'"{exe_path}" --silent'

        # Normal python execution
        python_executable = Path(sys.executable)
        pythonw_executable = python_executable.with_name("pythonw.exe")
        
        if pythonw_executable.exists():
            exec_path = pythonw_executable
        else:
            exec_path = python_executable

        project_root = Path(__file__).resolve().parent.parent
        main_py = project_root / "main.py"

        return f'"{exec_path}" "{main_py}" --silent'

    def is_enabled(self) -> bool:
        """Check if autostart is enabled with the correct command."""
        current_command = self._registry.get_command()
        expected_command = self.get_launch_command()
        return current_command == expected_command

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable autostart."""
        if enabled:
            command = self.get_launch_command()
            self._registry.set_command(command)
        else:
            self._registry.remove()
