@echo off
REM ============================================================
REM  True Morocco Journeys — ONE-TIME SETUP (Windows)
REM  Run this ONCE after unzipping the project.
REM  Double-click or run from CMD inside the backend\ folder.
REM ============================================================

echo.
echo === Step 1: Installing Python dependencies ===
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)

echo.
echo === Step 2: Applying database migrations ===
py -3.12 manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo ERROR: migrate failed.
    pause
    exit /b 1
)

echo.
echo === Step 3: Creating admin superuser ===
echo You will be asked for a username, email, and password.
echo Use these to log into http://localhost:8000/admin/
py -3.12 manage.py createsuperuser

echo.
echo ============================================================
echo  Setup complete!
echo  Now run start.bat to launch both servers.
echo ============================================================
pause
