# True Morocco Journeys

Multi-page travel agency website — static HTML/CSS/JS frontend + Django REST API backend.

---

## Quick start (3 steps)

### Step 1 — One-time setup
Open a terminal **inside the `backend/` folder** and run:

**Windows:**
```
setup.bat
```
**Mac / Linux:**
```
chmod +x setup.sh && ./setup.sh
```

This does three things automatically:
- `pip install -r requirements.txt` — installs Django + all dependencies
- `python manage.py migrate` — creates the SQLite database tables
- `python manage.py createsuperuser` — creates your admin login

### Step 2 — Start both servers
From the **project root folder** (where `index.html` lives):

**Windows:**
```
start.bat
```
**Mac / Linux:**
```
./start.sh
```

Or manually (two separate terminals):

| Terminal | Command | URL |
|---|---|---|
| 1 — Frontend | `python serve.py` | http://localhost:5500 |
| 2 — Backend | `cd backend && python manage.py runserver 8000` | http://localhost:8000 |

> ⚠️ **Both must be running at the same time.** Django on 8000, frontend on 5500.
> Do NOT run the frontend on 8000 — that port belongs to Django.

### Step 3 — Verify it works
Open your browser:
- **Website:** http://localhost:5500/index.html
- **API health check:** http://localhost:8000/api/health/  → `{"status":"ok"}`
- **Django admin:** http://localhost:8000/admin/ (use the credentials from setup)

---

## Project structure

```
true-morocco-journeys/
├── index.html               Home page
├── tours.html               Tours listing with live filter/search
├── tour-detail.html         Tour detail (tabbed, booking form)
├── destinations.html        9 destination profiles
├── about.html               Story, team, stats
├── blog.html                Blog listing with sidebar
├── blog-post.html           Sample article
├── contact.html             Validated contact form → Django API
│
├── css/style.css            All custom styles & design tokens
├── js/main.js               Navbar, reveals, counters, form → API
│
├── images/                  All placeholder images
│
├── serve.py                 Frontend dev server (port 5500)
├── start.bat / start.sh     Launch both servers in one click
│
└── backend/
    ├── manage.py
    ├── requirements.txt
    ├── setup.bat / setup.sh     One-time install + migrate
    ├── .env                     ← your secrets live here
    │
    ├── api/
    │   ├── views.py             POST /api/contact/ /booking/ /newsletter/
    │   ├── serializers.py       Input validation
    │   ├── models.py            NewsletterSubscriber
    │   ├── urls.py
    │   └── admin.py
    │
    ├── config/
    │   └── settings.py          Django settings (reads from .env)
    │
    └── templates/emails/
        ├── contact_admin.html   Email sent to you on each enquiry
        ├── contact_client.html  Confirmation email to the visitor
        ├── booking_admin.html
        ├── booking_client.html
        └── newsletter_welcome.html
```

---

## Environment variables (`.env`)

The `.env` file is already pre-filled for you in `backend/.env`.
Only two things you might need to change:

| Variable | What it is |
|---|---|
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail **App Password** (16 chars, no spaces) |
| `ADMIN_EMAIL` | Where contact/booking emails get delivered |

### Gmail App Password setup
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password (name it "TMJ Website")
3. Copy the 16-character code (remove spaces) into `.env`

> ⚠️ Never commit `.env` to git. It's already in `.gitignore`.

---

## API endpoints

| Method | Endpoint | Fields |
|---|---|---|
| GET | `/api/health/` | — |
| POST | `/api/contact/` | name, email, phone, subject, message |
| POST | `/api/booking/` | name, email, phone, tour_name, travel_date, num_people, message |
| POST | `/api/newsletter/` | email |

All POST endpoints return:
```json
{ "success": true,  "message": "..." }
{ "success": false, "error": "..." }
```

---

## Viewing submissions in Django admin

1. Go to http://localhost:8000/admin/
2. Log in with the superuser you created during setup
3. **Newsletter Subscribers** lists every email that subscribed
4. Contact and booking submissions are emailed to `ADMIN_EMAIL` and logged to `backend/tmj.log`

---

## Replacing placeholder images

All images under `images/` are generated artwork. Replace them with real photos — same filename, same folder, no HTML changes needed.

To regenerate the placeholder set (e.g. after changing the colour palette):
```bash
pip install pillow numpy
python scripts/generate_placeholder_images.py
```

---

## Design tokens

All brand colours are at the top of `css/style.css`:

```css
--color-primary:   #cc5500;   /* rust/orange — CTAs   */
--color-secondary: #004d40;   /* dark teal            */
--color-gold:      #d4a843;   /* accent               */
```
