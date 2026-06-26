#!/usr/bin/env python3
"""
serve.py — zero-dependency local preview server for the True Morocco
Journeys static frontend.

Usage:
    python serve.py          # http://localhost:5500  (default)
    python serve.py 3000     # any other port you prefer

IMPORTANT: the Django backend must run separately on port 8000.
  Terminal 1 (frontend): python serve.py
  Terminal 2 (backend):  cd backend && python manage.py runserver 8000

Why 5500? The .env / CORS config already whitelists http://localhost:5500.
Using any other port requires you to also add it to FRONTEND_URL in .env.
"""
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
ROOT = Path(__file__).parent.resolve()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        # Suppress noisy request logs for a cleaner console
        pass


def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"\n✅  Frontend served at  {url}")
        print(f"⚙️   Make sure Django is running at  http://localhost:8000")
        print("    Press Ctrl+C to stop.\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
