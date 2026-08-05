@echo off
REM ========================================
REM NEXUS INFINITY REAL - QUICK INSTALL
REM ========================================
REM Setup veloce senza menu interattivo

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║      NEXUS INFINITY REAL - QUICK INSTALL              ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRORE: Python non trovato!
    echo Scarica da: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Crea venv
if not exist "venv" (
    echo 🔧 Creazione ambiente virtuale...
    python -m venv venv
)

REM Attiva venv
call venv\Scripts\activate.bat

REM Installa dipendenze
echo 📦 Installazione dipendenze...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

REM Crea .env
if not exist ".env" (
    echo 🔑 Creazione file .env...
    (
        echo GROQ_API_KEY=your_groq_api_key_here
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo API_DEBUG=false
        echo DATABASE_URL=sqlite:///nexus.db
        echo SECURITY_LEVEL=high
        echo ENABLE_AUDIT_LOG=true
    ) > .env
)

echo.
echo ✅ Setup completato!
echo.
echo Comandi disponibili:
echo   - START_NEXUS.bat   : Menu interattivo
echo   - start.bat         : Avvio veloce
echo   - python main.py    : CLI diretta
echo   - python api_server.py : API Server
echo.
pause
