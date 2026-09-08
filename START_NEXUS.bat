@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

set "MODE=all"
if /i "%~1"=="--cli" set "MODE=cli"
if /i "%~1"=="--api" set "MODE=api"
if /i "%~1"=="--all" set "MODE=all"
if /i "%~1"=="--install-only" set "MODE=install"

echo ============================================================
echo NEXUS INFINITY REAL - SAFE SETUP AND START
echo ============================================================

call :find_python
if errorlevel 1 exit /b 1

echo [1/5] Python command: %PYTHON_CMD%
if not exist ".venv\Scripts\python.exe" (
    echo [2/5] Creating isolated Python environment...
    call %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: virtual environment creation failed.
        exit /b 1
    )
) else (
    echo [2/5] Existing Python environment found.
)

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
echo [3/5] Installing dependencies...
"%VENV_PY%" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 exit /b 1
"%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo ERROR: dependency installation failed.
    exit /b 1
)

echo [4/5] Checking local configuration...
if not exist ".env" copy /y ".env.example" ".env" >nul
findstr /b /c:"GROQ_API_KEY=gsk_" ".env" >nul 2>&1
if errorlevel 1 call :configure_groq
if errorlevel 1 exit /b 1

"%VENV_PY%" -c "from dotenv import dotenv_values; c=dotenv_values('.env'); k=c.get('GROQ_API_KEY',''); assert k.startswith('gsk_') and len(k)>20, 'invalid GROQ_API_KEY'"
if errorlevel 1 (
    echo ERROR: GROQ_API_KEY is missing or invalid in .env.
    exit /b 1
)
set "API_PORT=8000"
for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"API_PORT=" ".env"') do set "API_PORT=%%B"

echo [5/5] Running offline self-tests...
"%VENV_PY%" -m unittest -q test_nexus.py
if errorlevel 1 (
    echo ERROR: self-tests failed. Nexus was not started.
    exit /b 1
)

if /i "%MODE%"=="install" (
    echo Setup completed. No service was started.
    exit /b 0
)

if /i "%MODE%"=="cli" goto run_cli
if /i "%MODE%"=="api" goto run_api

echo Starting API in a separate window...
start "Nexus API" /D "%CD%" "%ComSpec%" /k ""%VENV_PY%" api_server.py"
call :wait_for_api
if errorlevel 1 exit /b 1
start "" "http://127.0.0.1:%API_PORT%/docs"
goto run_cli

:run_api
echo API documentation: http://127.0.0.1:%API_PORT%/docs
"%VENV_PY%" api_server.py
exit /b %errorlevel%

:run_cli
echo Starting Nexus CLI. Type exit to stop the CLI.
"%VENV_PY%" main.py
exit /b %errorlevel%

:find_python
set "PYTHON_CMD="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"
if defined PYTHON_CMD exit /b 0
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"
if defined PYTHON_CMD exit /b 0

echo Python 3 was not found.
where winget >nul 2>&1
if errorlevel 1 (
    echo Install Python 3.11 or newer from https://www.python.org/downloads/
    exit /b 1
)
choice /c YN /n /m "Install Python 3.12 automatically with winget? [Y/N] "
if errorlevel 2 exit /b 1
winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements
if errorlevel 1 exit /b 1
py -3 --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
    echo Python was installed, but this terminal cannot see it yet.
    echo Close this window and run START_NEXUS.bat again.
    exit /b 1
)
exit /b 0

:configure_groq
echo A Groq API key is required. The key is saved only in the local .env file.
set "GROQ_KEY="
if defined GROQ_API_KEY set "GROQ_KEY=%GROQ_API_KEY%"
if defined GROQ_KEY goto validate_groq_key
for /f "usebackq delims=" %%K in (`powershell.exe -NoProfile -Command "$s=Read-Host 'Paste the new Groq API key' -AsSecureString; $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try {[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b)} finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"`) do set "GROQ_KEY=%%K"
if not defined GROQ_KEY (
    echo ERROR: no key was entered.
    exit /b 1
)
:validate_groq_key
set "GROQ_PREFIX=%GROQ_KEY:~0,4%"
if /i not "%GROQ_PREFIX%"=="gsk_" (
    set "GROQ_KEY="
    echo ERROR: the Groq key format is not valid.
    exit /b 1
)
powershell.exe -NoProfile -Command "$p='.env'; $lines=Get-Content -LiteralPath $p; $found=$false; $out=@($lines | ForEach-Object { if ($_ -match '^GROQ_API_KEY=') {$found=$true; 'GROQ_API_KEY=' + $env:GROQ_KEY} else {$_} }); if (-not $found) {$out += 'GROQ_API_KEY=' + $env:GROQ_KEY}; Set-Content -LiteralPath $p -Value $out -Encoding utf8"
set "GROQ_KEY="
if errorlevel 1 (
    echo ERROR: .env could not be updated.
    exit /b 1
)
exit /b 0

:wait_for_api
for /l %%I in (1,1,30) do (
    powershell.exe -NoProfile -Command "try {$r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:%API_PORT%/api/status' -TimeoutSec 2; if ($r.StatusCode -eq 200) {exit 0}} catch {}; exit 1" >nul 2>&1
    if not errorlevel 1 (
        echo API is online: http://127.0.0.1:%API_PORT%/docs
        exit /b 0
    )
    timeout /t 1 /nobreak >nul
)
echo ERROR: API did not become healthy within 30 seconds.
exit /b 1
