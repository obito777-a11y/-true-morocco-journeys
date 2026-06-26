@echo off
REM ============================================================
REM  True Morocco Journeys — START BOTH SERVERS (Windows)
REM  Run from the project ROOT folder (where index.html lives).
REM  Opens two CMD windows: one for Django, one for the frontend.
REM ============================================================

echo Starting Django backend on http://localhost:8000 ...
start "TMJ Django Backend" cmd /k "cd backend && py -3.12 manage.py runserver 8000"

echo Waiting 3 seconds for Django to start...
timeout /t 3 /nobreak >nul

echo Starting frontend server on http://localhost:5500 ...
start "TMJ Frontend" cmd /k "py -3.12 serve.py 5500"

echo.
echo ============================================================
echo  Both servers started in separate windows.
echo  Frontend:  http://localhost:5500
echo  Backend:   http://localhost:8000/api/health/
echo  Admin:     http://localhost:8000/admin/
echo ============================================================
