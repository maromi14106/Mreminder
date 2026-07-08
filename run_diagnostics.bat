@echo off
setlocal
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)
echo =========================================
echo 1. Environment Info
echo =========================================
where.exe python
python -c "import sys, struct; print(sys.executable); print(sys.version); print(f'Architecture: {struct.calcsize(\"P\") * 8}bit')"
python -c "import PySide6, shiboken6; print(f'PySide6: {PySide6.__version__}'); print(f'shiboken6: {shiboken6.__version__}')"
python -m PyInstaller --version
python -m pip show PyInstaller pyinstaller-hooks-contrib PySide6 shiboken6
python -m pip check

echo =========================================
echo 2. Update PyInstaller
echo =========================================
python -m pip install --upgrade PyInstaller pyinstaller-hooks-contrib

echo =========================================
echo 3. Clean Build Folders
echo =========================================
powershell -Command "Remove-Item build -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item dist -Recurse -Force -ErrorAction SilentlyContinue"

echo =========================================
echo 4. Build Probes
echo =========================================
python -m PyInstaller --clean --noconfirm --onedir --console --noupx tools\diagnostics\probe_python.py
python -m PyInstaller --clean --noconfirm --onedir --console --noupx tools\diagnostics\probe_qtwidgets.py
python -m PyInstaller --clean --noconfirm --onedir --console --noupx tools\diagnostics\probe_qtnetwork.py
python -m PyInstaller --clean --noconfirm --onedir --console --noupx tools\diagnostics\probe_qtmultimedia.py

echo =========================================
echo 5. Build Mreminder-debug
echo =========================================
python -m PyInstaller --clean --noconfirm Mreminder-debug.spec

echo =========================================
echo 6. Run Tests and Linters
echo =========================================
python -m pytest -q
python -m ruff check .
python -m black .

echo =========================================
echo Diagnostics Setup Complete.
echo Please manually run the built executables in the dist folder:
echo - dist\probe_python\probe_python.exe
echo - dist\probe_qtwidgets\probe_qtwidgets.exe
echo - dist\probe_qtnetwork\probe_qtnetwork.exe
echo - dist\probe_qtmultimedia\probe_qtmultimedia.exe
echo - dist\Mreminder-debug\Mreminder-debug.exe
echo =========================================

