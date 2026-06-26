#!/usr/bin/env bash
# ============================================================
#  True Morocco Journeys — ONE-TIME SETUP (Mac / Linux)
#  Run this ONCE after unzipping the project.
#  cd backend && chmod +x setup.sh && ./setup.sh
# ============================================================
set -e

echo ""
echo "=== Step 1: Installing Python dependencies ==="
pip install -r requirements.txt

echo ""
echo "=== Step 2: Applying database migrations ==="
py -3.12 manage.py migrate

echo ""
echo "=== Step 3: Creating admin superuser ==="
echo "You will be asked for a username, email and password."
echo "Use these to log into http://localhost:8000/admin/"
py -3.12 manage.py createsuperuser

echo ""
echo "============================================================"
echo " Setup complete!"
echo " Now run:  ./start.sh   (or start.bat on Windows)"
echo "============================================================"
