@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment Python 3.11...
    uv venv .venv --python 3.11 || py -3.11 -m venv .venv || goto :error
    uv pip install --python .venv\Scripts\python.exe -r requirements.txt || .venv\Scripts\python.exe -m pip install -r requirements.txt || goto :error
)
.venv\Scripts\python.exe main.py
pause
exit /b 0

:error
echo Gagal menyiapkan environment. Pastikan Python 3.11 atau uv terpasang.
pause
exit /b 1
