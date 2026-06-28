# True Morocco Journeys

A complete, multi-page static website for a Moroccan travel agency, built with HTML5, Bootstrap 5, custom CSS and vanilla JavaScript.

> **Heads up on imagery:** every photo in this build is a generated placeholder (gradient + simple Moroccan-motif illustration + a caption telling you what it represents — e.g. "Hassan II Mosque, Casablanca"). They exist so the layout, crops and colour balance are easy to judge before real photography is dropped in. See **Replacing the placeholder photography** below.

---

## 1. What's included

```
true-morocco-journeys/
├── index.html              Home page
├── tours.html               Tours & Excursions listing (with filter/search)
├── tour-detail.html         Sample tour detail page (Sahara 4x4 Expedition)
├── destinations.html        Destinations grid + 9 destination profiles
├── about.html                About Us (story, values, team, stats)
├── blog.html                 Blog listing with sidebar
├── blog-post.html            Sample blog article
├── contact.html              Contact form, info cards, map placeholder, FAQ
│
├── css/
│   └── style.css             All custom styles (design tokens at the top)
├── js/
│   └── main.js                Navbar scroll state, reveal animations, counters,
│                               tour filters, form validation, back-to-top
├── images/                    All placeholder photography (see below)
│   ├── hero/                  Page header banners
│   ├── tours/                 Tour card images
│   ├── destinations/          Destination card images
│   ├── blog/                  Blog thumbnails
│   ├── team/                  Team & testimonial avatars
│   ├── gallery/                Instagram-style gallery strip
│   ├── logo.png / favicon.png
│   └── og-image.jpg           Social-share preview image
│
├── scripts/
│   └── generate_placeholder_images.py   Regenerates every placeholder image
│
├── backend/                   OPTIONAL example backend (see section 5)
│   ├── app.py
│   └── requirements.txt
│
├── serve.py                   Zero-dependency local preview server
└── README.md                  This file
```

This is a fully static site — **no build step, no npm install required.** Bootstrap 5, Bootstrap Icons and Google Fonts are loaded via CDN `<link>`/`<script>` tags directly in each HTML file.

---

## 2. Previewing the site locally

You need a local server (not `file://`) so relative paths and fonts behave correctly. Two easy options:

**Option A — the included Python script (no dependencies):**
```bash
python3 serve.py          # serves at http://localhost:8000
python3 serve.py 5050     # or pick your own port
```

**Option B — any static server you already have:**
```bash
npx serve .
# or
php -S localhost:8000
```

Then open `http://localhost:8000/index.html`.

---

## 3. Design system

Defined as CSS custom properties at the top of `css/style.css` — change these once and the whole site updates:

| Token | Value | Use |
|---|---|---|
| `--color-primary` | `#cc5500` | Rust/orange — primary CTAs, links, accents |
| `--color-secondary` | `#004d40` | Dark teal — secondary buttons, stats band, footer accents |
| `--color-navy` | `#1a2238` | Primary text colour |
| `--color-gold` | `#d4a843` | Sparing accent — eyebrows, hero highlight word, star ratings |
| `--color-sand` | `#f3e9da` | Warm section background |

**Typography:** Montserrat (headings, via Google Fonts) / Open Sans (body text). Both are loaded with `font-display: swap` for performance.

**Signature element — the keyhole arch:** Moroccan architecture uses a distinctive horseshoe/keyhole arch silhouette throughout — the logo, the `.arch-image-wrap` image frames (see the About page story image or any destination profile), and the circular "day number" badges in the tour itinerary. This is the one recurring motif tying the brand together, rather than a generic rounded-corner card everywhere.

---

## 4. Replacing the placeholder photography

Every image keeps its final filename and aspect ratio already wired into the layout, so real photography is a drop-in replacement — same filename, same folder, no HTML changes needed:

- `images/hero/hero-home.jpg` → 1920×950 landscape (Hassan II Mosque or similar landmark)
- `images/hero/hero-*.jpg` → 1920×560 landscape (other page banners)
- `images/tours/*.jpg` and `images/destinations/*.jpg` → roughly 4:3, 900×680 or larger
- `images/blog/*.jpg` → 16:10, 900×620 or larger
- `images/gallery/*.jpg` → square, 700×700 or larger
- `images/team/team-*.jpg` → square headshots
- `images/logo.png` → transparent PNG, ~360×360 (replace with your real mark)

If you'd rather regenerate a fresh, on-brand set of placeholders (e.g. after changing the colour palette) instead of hand-replacing each file:
```bash
pip install pillow numpy --break-system-packages   # or use a virtualenv
python3 scripts/generate_placeholder_images.py
```

---

## 5. The contact form (and the optional Flask backend)

Out of the box, `contact.html`'s form validates client-side (required fields, email format, consent checkbox) and shows a success message — but it doesn't send anywhere, since this is a static template. Look at `initContactForm()` in `js/main.js`.

If/when you want it to actually deliver enquiries, `backend/app.py` is a small, optional Flask example that:
- Validates the same fields server-side
- Logs every submission to `backend/contact_submissions.log`
- Emails the enquiry via SMTP if you set `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS` / `CONTACT_TO` environment variables

```bash
cd backend
pip install -r requirements.txt
export SMTP_HOST=smtp.yourprovider.com SMTP_PORT=587 \
       SMTP_USER=you@yourdomain.com SMTP_PASS=app-password \
       CONTACT_TO=hello@truemoroccojourneys.com
python3 app.py        # runs on http://localhost:5001
```

Then update the `fetch()` call in `initContactForm()` (in `js/main.js`) to `POST` to `http://localhost:5001/api/contact` instead of the simulated `setTimeout`. This part is intentionally left as a manual step since the right backend (Flask, a serverless function, Formspree, etc.) depends on where you're hosting the site.

---

## 6. Pages & key interactive features

- **Home** — hero, trust strip, featured tours, "why us", destination teasers, stats counters, testimonials, gallery, newsletter signup
- **Tours & Excursions** — 12 tour cards with a working category filter (Desert / Imperial Cities / Mountains / Coast) and live name search, both in `js/main.js`
- **Tour Detail** — image header, tabbed Overview / Itinerary / Inclusions / Reviews, sticky booking summary card
- **Destinations** — 9-card grid linking down to in-page destination profiles (anchor links)
- **About Us** — story, values, animated stats counters, team grid
- **Blog** — listing with sidebar (search, categories, recent posts, newsletter) + pagination UI
- **Blog Post** — full article layout with pull-quote styling, tags, share row, author box, static comments
- **Contact** — validated form, info cards, map placeholder (swap for a real embedded map iframe), FAQ accordion

All interactivity (navbar scroll state, scroll-reveal animations, counters, filters, form validation, back-to-top button) is in `js/main.js`, written in plain JavaScript with no dependencies beyond Bootstrap's own JS bundle (used for the navbar collapse, tabs and accordion).

---

## 7. Accessibility & performance notes

- Every image has descriptive `alt` text
- Visible focus rings on all interactive elements (`:focus-visible`)
- `prefers-reduced-motion` is respected — animations are disabled for users who request it
- Forms use proper `<label for>` associations and native HTML5 validation attributes
- Semantic landmarks (`<nav>`, `<header>`, `<main>`-equivalent sections, `<footer>`)

## 8. Adding a new tour or blog post

There's no templating engine here — duplicate the closest existing card markup:
- New tour → copy a `.tour-card` block in `tours.html`, give it a new `data-category` and `data-title`, and link its "View Details" button to a new detail page (duplicate `tour-detail.html` and edit the content).
- New blog post → copy a `.blog-card` block in `blog.html` and duplicate `blog-post.html` for the article page.

---

Built with HTML5, Bootstrap 5 (CDN), custom CSS and vanilla JavaScript.
