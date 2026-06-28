"""
backend/app.py — OPTIONAL example backend for the contact form.

The site itself is fully static (HTML/CSS/vanilla JS) and works without
this file. The contact form on contact.html currently simulates a
submission in the browser (see js/main.js -> initContactForm()).

This Flask app is a starting point if/when you want the form to actually
send mail. It validates the same fields the front-end does, then logs the
submission to contact_submissions.log and (optionally) emails it via SMTP
if you set the environment variables below.

Quick start:
    pip install -r backend/requirements.txt
    export SMTP_HOST=smtp.yourprovider.com
    export SMTP_PORT=587
    export SMTP_USER=you@yourdomain.com
    export SMTP_PASS=your-app-password
    export CONTACT_TO=hello@truemoroccojourneys.com
    python3 backend/app.py

Then point the form's JS fetch() call (see the commented example in
js/main.js) at POST http://localhost:5001/api/contact instead of the
simulated timeout.
"""
import os
import smtplib
import logging
from datetime import datetime, timezone
from email.mime.text import MIMEText

from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
except ImportError:  # pragma: no cover
    CORS = None

app = Flask(__name__)
if CORS:
    CORS(app)  # allow the static front-end (different origin in dev) to call this API

logging.basicConfig(
    filename="contact_submissions.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

REQUIRED_FIELDS = ["name", "email", "subject", "message"]


def send_email(payload: dict) -> bool:
    """Send the enquiry via SMTP if credentials are configured. Returns
    True on success, False if SMTP isn't configured or sending failed."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    to_addr = os.environ.get("CONTACT_TO", "hello@truemoroccojourneys.com")
    port = int(os.environ.get("SMTP_PORT", 587))

    if not all([host, user, password]):
        return False  # not configured — submission is still logged

    body = (
        f"New enquiry from the True Morocco Journeys contact form\n\n"
        f"Name: {payload['name']}\n"
        f"Email: {payload['email']}\n"
        f"Phone: {payload.get('phone', '-')}\n"
        f"Subject: {payload['subject']}\n\n"
        f"Message:\n{payload['message']}\n"
    )
    msg = MIMEText(body)
    msg["Subject"] = f"[Website] {payload['subject']}"
    msg["From"] = user
    msg["To"] = to_addr

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())
    return True


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or request.form
    missing = [f for f in REQUIRED_FIELDS if not (data.get(f) or "").strip()]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    payload = {k: data.get(k, "").strip() for k in ["name", "email", "phone", "subject", "message"]}
    logging.info("Submission: %s", payload)

    emailed = False
    try:
        emailed = send_email(payload)
    except Exception as exc:  # pragma: no cover — don't fail the request over SMTP issues
        logging.warning("Email send failed: %s", exc)

    return jsonify({
        "ok": True,
        "emailed": emailed,
        "received_at": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5001)), debug=True)
