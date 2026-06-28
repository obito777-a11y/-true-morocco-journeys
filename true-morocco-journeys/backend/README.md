# True Morocco Journeys — Django Backend

Production-ready REST API backend for the True Morocco Journeys travel agency website. Built with **Django 4.2+**, **Django REST Framework**, Gmail SMTP email, and rate limiting.

---

## Features

| Endpoint | Method | Description |
|---|---|---|
| `/api/health/` | GET | Liveness probe — returns status & timestamp |
| `/api/contact/` | POST | Contact form — notifies agency + confirms to client |
| `/api/booking/` | POST | Booking request — validates tour/date/people + sends emails |
| `/api/newsletter/` | POST | Newsletter subscribe — saves to DB + sends welcome email |

- **Rate limiting**: 10 requests per IP per 15 minutes on all POST endpoints
- **CORS**: Pre-configured for localhost dev + your production domain
- **Validation**: All fields validated server-side via DRF serializers
- **Emails**: Branded HTML templates with inline CSS (terracotta `#C8724A` + gold `#D4A853`)
- **Logging**: Every request logged to `tmj.log` and the console
- **Graceful errors**: Never crashes on bad input — always returns JSON

---

## Prerequisites

- Python 3.11 or higher
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) (not your regular password — 2-Step Verification must be enabled)

---

## Quick Start

### 1. Clone / navigate to the backend directory

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\activate             # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your-secret-key-here          # generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=True
PORT=8000
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # Gmail App Password (16 chars with spaces)
ADMIN_EMAIL=owner@youragency.com

AGENCY_NAME=True Morocco Journeys
AGENCY_PHONE=+212 XXX XXX XXX
AGENCY_WEBSITE=https://truemoroccojourney.com

FRONTEND_URL=http://localhost:5500,https://truemoroccojourney.com
```

> **Gmail App Password setup:**
> 1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
> 2. Enable 2-Step Verification if not already on
> 3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 4. Create a new app password → choose "Mail" → copy the 16-character password
> 5. Paste it (spaces included) as `EMAIL_HOST_PASSWORD`

### 5. Generate a secret key (if needed)

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output into `.env` as `SECRET_KEY`.

### 6. Run database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (for Django admin)

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

The API is now live at **http://localhost:8000/**.

---

## API Reference

### GET /api/health/

```bash
curl http://localhost:8000/api/health/
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-15T10:30:00.000000+00:00",
  "service": "True Morocco Journeys"
}
```

---

### POST /api/contact/

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | ✅ | 2–100 characters |
| `email` | string | ✅ | Valid email format |
| `phone` | string | ❌ | International format |
| `message` | string | ✅ | 10–3000 characters |

```bash
curl -X POST http://localhost:8000/api/contact/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Ahmed K.","email":"ahmed@example.com","message":"I would like to plan a 7-day Sahara tour for April."}'
```

**Success:**
```json
{"success": true, "message": "Thank you! Your message has been sent. We'll reply within one business day."}
```

**Error:**
```json
{"success": false, "error": "Enter a valid email address."}
```

---

### POST /api/booking/

**Body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | ✅ | 2–100 chars |
| `email` | string | ✅ | Valid email |
| `phone` | string | ❌ | International format |
| `tour_name` | string | ✅ | Name of the tour |
| `travel_date` | string | ✅ | `YYYY-MM-DD` or `DD/MM/YYYY`, must be in the future |
| `num_people` | integer | ✅ | 1–100 |
| `message` | string | ❌ | Additional notes |

```bash
curl -X POST http://localhost:8000/api/booking/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Sarah M.","email":"sarah@example.com","phone":"+44 7911 123456","tour_name":"Sahara Desert 4×4 Adventure","travel_date":"2025-04-20","num_people":2,"message":"We are celebrating our anniversary."}'
```

**Success:**
```json
{"success": true, "message": "Your booking request for Sahara Desert 4×4 Adventure has been received! We'll contact you within 24 hours to confirm availability."}
```

---

### POST /api/newsletter/

**Body (JSON):**

| Field | Type | Required |
|---|---|---|
| `email` | string | ✅ |

```bash
curl -X POST http://localhost:8000/api/newsletter/ \
  -H "Content-Type: application/json" \
  -d '{"email":"traveller@example.com"}'
```

**Success:**
```json
{"success": true, "message": "You're subscribed! Welcome to our newsletter."}
```

---

## Frontend Integration

In your static HTML frontend, use `fetch()` with JSON:

```javascript
// Contact form example
async function submitContact(formData) {
  try {
    const response = await fetch('http://localhost:8000/api/contact/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: formData.name,
        email: formData.email,
        phone: formData.phone || '',
        message: formData.message,
      }),
    });
    const data = await response.json();
    if (data.success) {
      // Show success message
    } else {
      // Show data.error to the user
    }
  } catch (err) {
    console.error('Network error:', err);
  }
}
```

---

## Django Admin

The admin panel is available at **http://localhost:8000/admin/**

Log in with the superuser credentials you created. From here you can:
- View all newsletter subscribers
- Activate / deactivate subscriber records
- Search by email

---

## Project Structure

```
backend/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── tmj.log                        ← created on first run
├── db.sqlite3                     ← created after migrate
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/
│   ├── __init__.py
│   ├── models.py                  ← NewsletterSubscriber model
│   ├── serializers.py             ← Input validation
│   ├── views.py                   ← Business logic + email dispatch
│   ├── urls.py
│   └── admin.py
└── templates/
    └── emails/
        ├── contact_admin.html
        ├── contact_client.html
        ├── booking_admin.html
        ├── booking_client.html
        └── newsletter_welcome.html
```

---

## Rate Limiting

All POST endpoints are rate-limited to **10 requests per 15 minutes per IP address** using `django-ratelimit`. When the limit is exceeded the API returns HTTP `403`. You can adjust this in `api/views.py` by changing the `rate` parameter:

```python
@ratelimit(key="ip", rate="10/15m", method="POST", block=True)
```

Common rate strings: `"5/m"` (5/min), `"100/h"` (100/hour), `"10/15m"` (10 per 15 min).

---

## Production Deployment

### Environment changes for production

In `.env`:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=<long-random-secret>
FRONTEND_URL=https://yourdomain.com
```

### Collect static files

```bash
python manage.py collectstatic --noinput
```

### Use Gunicorn + Nginx

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Point Nginx to `localhost:8000` and handle SSL termination there.

---

## Troubleshooting

### Emails not sending

1. Make sure `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set in `.env`
2. Confirm you're using a Gmail **App Password** (not your account password)
3. Check `tmj.log` for `Email FAILED` lines with the specific SMTP error
4. To test without real email, set in `settings.py`:
   ```python
   EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
   ```
   This prints emails to the terminal instead of sending them.

### CORS errors in browser

Add your frontend's origin to `FRONTEND_URL` in `.env`:
```env
FRONTEND_URL=http://localhost:5500,http://127.0.0.1:5500,https://yoursite.com
```

If you're opening `index.html` directly from the filesystem (no server), add `null` to `CORS_ALLOWED_ORIGINS` in `settings.py` (already included by default in DEBUG mode).

### Rate limit triggered during development

You can temporarily raise the limit or disable it in `api/views.py`:
```python
@ratelimit(key="ip", rate="1000/h", method="POST", block=True)
```

---

## License

MIT — free to use and modify for your project.
