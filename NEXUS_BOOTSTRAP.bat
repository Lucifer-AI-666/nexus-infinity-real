@echo off
setlocal EnableExtensions DisableDelayedExpansion

rem Nexus Infinity Real - standalone Windows bootstrap.
rem It downloads/updates the repository, prepares Python, and starts the full stack.

set "REPO_URL=https://github.com/Lucifer-AI-666/nexus-infinity-real.git"
set "ARCHIVE_URL=https://github.com/Lucifer-AI-666/nexus-infinity-real/archive/refs/heads/main.zip"
set "SCRIPT_DIR=%~dp0"
set "INSTALL_DIR=%SCRIPT_DIR%nexus-infinity-real"

if exist "%SCRIPT_DIR%main.py" if exist "%SCRIPT_DIR%requirements.txt" (
    set "INSTALL_DIR=%SCRIPT_DIR%"
    goto repo_ready
)

echo [1/3] Download or update Nexus Infinity Real...
if exist "%INSTALL_DIR%\.git" (
    git -C "%INSTALL_DIR%" fetch origin main
    if errorlevel 1 goto download_error
    git -C "%INSTALL_DIR%" merge --ff-only origin/main
    if errorlevel 1 (
        echo ERROR: local changes prevent a safe automatic update.
        echo Resolve them in "%INSTALL_DIR%" and run this file again.
        exit /b 1
    )
    goto repo_ready
)

where git >nul 2>&1
if not errorlevel 1 (
    git clone --depth 1 "%REPO_URL%" "%INSTALL_DIR%"
    if errorlevel 1 goto download_error
    goto repo_ready
)

where powershell.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git and Windows PowerShell are both unavailable.
    echo Install Git from https://git-scm.com/download/win and retry.
    exit /b 1
)

set "ZIP_FILE=%TEMP%\nexus-infinity-real-%RANDOM%.zip"
set "EXTRACT_DIR=%TEMP%\nexus-infinity-real-%RANDOM%"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Invoke-WebRequest -UseBasicParsing -Uri $env:ARCHIVE_URL -OutFile $env:ZIP_FILE; Expand-Archive -LiteralPath $env:ZIP_FILE -DestinationPath $env:EXTRACT_DIR -Force; Move-Item -LiteralPath (Join-Path $env:EXTRACT_DIR 'nexus-infinity-real-main') -Destination $env:INSTALL_DIR"
if errorlevel 1 goto download_error
del /q "%ZIP_FILE%" >nul 2>&1
rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1

:repo_ready
if not exist "%INSTALL_DIR%\START_NEXUS.bat" (
    echo ERROR: START_NEXUS.bat was not found in "%INSTALL_DIR%".
    exit /b 1
)

echo [2/3] Repository ready: %INSTALL_DIR%
echo [3/3] Preparing and starting the complete system...
call "%INSTALL_DIR%\START_NEXUS.bat" --all
exit /b %errorlevel%

:download_error
echo ERROR: Nexus could not be downloaded or updated.
echo Check the internet connection and retry.
exit /b 1

