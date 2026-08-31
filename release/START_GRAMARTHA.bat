@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "APP_URL=http://127.0.0.1:8765/ui/"
set "HEALTH_URL=http://127.0.0.1:8765/health"
set "VENV=%CD%\.gramartha-venv"
set "LOG=%CD%\gramartha-local.log"

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  set "PYTHON_CMD=py -3.12"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.12+ is required. Install Python and run this file again.
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
)

%PYTHON_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,12) else 1)" >nul 2>nul
if errorlevel 1 (
  echo Python 3.12+ is required.
  pause
  exit /b 1
)

if not exist "%VENV%\Scripts\python.exe" (
  echo Preparing GramArtha for first launch...
  %PYTHON_CMD% -m venv "%VENV%"
  if errorlevel 1 goto :fail
  "%VENV%\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto :fail
  "%VENV%\Scripts\python.exe" -m pip install .
  if errorlevel 1 goto :fail
)

if not exist "%CD%\data\sih26091_phase2.sqlite" (
  echo The Judge Package runtime database is missing. Re-download the release ZIP.
  pause
  exit /b 1
)
if not exist "%CD%\data\west_bengal_osm.sqlite" (
  echo The Judge Package OSM runtime database is missing. Re-download the release ZIP.
  pause
  exit /b 1
)

powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing '%HEALTH_URL%' -TimeoutSec 2 ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if errorlevel 1 (
  echo Starting GramArtha...
  set "SIH26091_SQLITE_PATH=%CD%\data\sih26091_phase2.sqlite"
  set "SIH26091_OSM_SQLITE_PATH=%CD%\data\west_bengal_osm.sqlite"
  start "GramArtha Local Service" /min cmd /c ""%VENV%\Scripts\python.exe" -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8765 > "%LOG%" 2>&1"

  for /L %%I in (1,1,40) do (
    powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing '%HEALTH_URL%' -TimeoutSec 2 ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
    if !ERRORLEVEL!==0 goto :ready
    timeout /t 1 /nobreak >nul
  )
  goto :fail
)

:ready
start "" "%APP_URL%"
echo GramArtha is running at %APP_URL%
echo Log: %LOG%
pause
exit /b 0

:fail
echo GramArtha could not be prepared or started. Check your Python installation and %LOG%.
pause
exit /b 1
