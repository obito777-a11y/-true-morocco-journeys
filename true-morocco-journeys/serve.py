#!/usr/bin/env python3
"""
serve.py — zero-dependency local preview server for the True Morocco
Journeys static site.

Usage:
    python3 serve.py            # serves on http://localhost:8000
    python3 serve.py 5000       # serves on http://localhost:5000

This uses only Python's standard library (http.server), so there is
nothing to install. Stop the server with Ctrl+C.
"""
import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = Path(__file__).parent.resolve()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        # Avoid aggressive caching while you're actively editing files.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"Serving True Morocco Journeys at {url}")
        print("Press Ctrl+C to stop.")
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
