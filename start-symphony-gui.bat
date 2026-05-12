@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found on PATH.
  echo Install Node.js or run this from an environment where node is available.
  pause
  exit /b 1
)

echo Starting SpriteMake Mini-Symphony GUI...
echo A free local port will be selected automatically.
echo Live log will be written to output\SYMPHONY-GUI.log.
echo.

node tools\symphony-gui\server.js

echo.
echo SpriteMake Mini-Symphony GUI stopped.
pause
