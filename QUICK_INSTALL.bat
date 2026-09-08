@echo off
call "%~dp0START_NEXUS.bat" --install-only
exit /b %errorlevel%
