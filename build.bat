@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment Python not found.
    exit /b 1
)

echo =========================================
echo 1. Check Dependencies and Environment
echo =========================================
".venv\Scripts\python.exe" -c "import sys, PyInstaller, PySide6, shiboken6; print(f'sys.executable: {sys.executable}'); print(f'sys.prefix: {sys.prefix}'); print(f'PyInstaller: {PyInstaller.__version__}'); print(f'PySide6: {PySide6.__version__}'); print(f'shiboken6: {shiboken6.__version__}')"
if errorlevel 1 (
    echo [ERROR] Dependency check failed.
    exit /b 1
)

echo =========================================
echo 2. Clean Build Folders
echo =========================================
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo =========================================
echo 3. Build Mreminder
echo =========================================
".venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm Mreminder.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

echo =========================================
echo 4. Verify Build Artifact
echo =========================================
if not exist "dist\Mreminder\Mreminder.exe" (
    echo [ERROR] Mreminder.exe not found.
    exit /b 1
)

echo [SUCCESS] Build completed successfully.
exit /b 0