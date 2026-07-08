@echo off
setlocal
cd /d "%~dp0"

echo =========================================
echo 1. Running Tests and Linters...
echo =========================================
".venv\Scripts\python.exe" -m pytest -q
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m ruff check .
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m black --check .
if errorlevel 1 exit /b 1

echo =========================================
echo 2. Checking Environment...
echo =========================================
".venv\Scripts\python.exe" -m PyInstaller --version
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m pip check
if errorlevel 1 exit /b 1

echo =========================================
echo 3. Running Build...
echo =========================================
call build.bat
if errorlevel 1 exit /b 1

echo [SUCCESS] All checks and build passed.
exit /b 0