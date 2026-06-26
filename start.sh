#!/usr/bin/env bash
# ============================================================
#  True Morocco Journeys — START BOTH SERVERS (Mac / Linux)
#  Run from the project ROOT folder:  chmod +x start.sh && ./start.sh
# ============================================================
set -e

echo "Starting Django backend on http://localhost:8000 ..."
cd backend
py -3.12 manage.py runserver 8000 &
DJANGO_PID=$!
cd ..

echo "Waiting 2 seconds for Django to initialise..."
sleep 2

echo "Starting frontend on http://localhost:5500 ..."
py -3.12 serve.py 5500 &
FRONTEND_PID=$!

echo ""
echo "============================================================"
echo " Frontend:  http://localhost:5500"
echo " Backend:   http://localhost:8000/api/health/"
echo " Admin:     http://localhost:8000/admin/"
echo " Press Ctrl+C to stop both servers."
echo "============================================================"

# Wait for either process to exit, then kill both
wait $DJANGO_PID $FRONTEND_PID
trap "kill $DJANGO_PID $FRONTEND_PID 2>/dev/null" EXIT
