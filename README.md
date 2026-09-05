# Credentia — Internship Certificate Provider

A Django platform for running task-based internship programs: interns register,
work through company-defined task modules, and unlock a company-branded offer
letter and payment-gated certificate. Companies manage everything — tracks,
tasks, pricing, and the certificate/offer-letter designs — from a private
portal with no public registration.

Full project rationale and day-by-day build plan: see the accompanying
`Internship_Certificate_Provider_Project_Report.docx`.

## Stack

Python · Django 6 · SQLite (dev) / PostgreSQL (prod-ready via `DATABASE_URL`) ·
Tailwind-free hand-built design system (CSS custom properties) · vanilla JS ·
Razorpay · WeasyPrint (PDF generation)

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then fill in DJANGO_SECRET_KEY at minimum
python3 manage.py migrate
python3 manage.py seed_demo # creates a demo track, tasks, default certificate
                             # design, and a company login (see output for the
                             # generated password — change it immediately)
python3 manage.py runserver
```

Visit:
- `http://127.0.0.1:8000/` — public site
- `http://127.0.0.1:8000/accounts/register/` — intern sign-up
- `http://127.0.0.1:8000/<COMPANY_PORTAL_SLUG>/login/` — company portal
  (default slug is `mgmt-9f21`, set in `.env`)

`python3 manage.py createsuperuser` also gets you into `/django-admin/` for
quick data fixes — but day-to-day track/task/template management should go
through the company portal, which is the intended surface per the brief.

## Windows notes

**Always run from `.env`, not a bare `runserver`.** Copy `.env.example` to
`.env` before your first run. If Django can't find `.env` it now defaults to
`DJANGO_DEBUG=True`, so you'll get a working local server either way — but a
missing `.env` in production would silently disable every hardening setting
described below, so don't skip this step.

**PDF generation just works on Windows out of the box.** Certificate/offer
letter PDFs are generated through `certificates/pdf.py`, which tries
WeasyPrint first and automatically falls back to the pure-Python `xhtml2pdf`
if WeasyPrint's native GTK/Pango/Cairo libraries aren't installed (the
`cannot load library 'libgobject-2.0-0'` error is exactly this — Windows
doesn't ship those libraries, and installing them isn't required). Both
engines render the shipped certificate/offer-letter designs correctly. If
you want WeasyPrint's slightly higher-fidelity output on Windows too, install
the [GTK3 runtime for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer)
— optional, not required.

If you're designing your **own** certificate/offer-letter upload, prefer
`<table>`-based layout over `flexbox`/`grid` for maximum compatibility with
the xhtml2pdf fallback path (see the two `default-seed/index.html` files for
the pattern) — WeasyPrint handles modern CSS fine either way.

## If your browser gets stuck forcing HTTPS on localhost

This happens if the server ever ran with `DEBUG=False` (e.g. no `.env` was
present) — it sends an HSTS header that tells the browser to force HTTPS for
that host for the next year, and the dev server only speaks plain HTTP, so
every request after that fails. Two ways out:
- Easiest: browse to `http://localhost:8000/` instead of `127.0.0.1:8000` —
  different hostname, unaffected by the existing HSTS pin.
- Permanent: in Chrome, visit `chrome://net-internals/#hsts`, enter
  `127.0.0.1` under "Delete domain security policies", and delete it.

## Project layout

```
config/          settings, root urls
core/            public marketing pages (home, track listing/detail, about)
accounts/        intern registration, login, the 4-tab dashboard
company/         hidden-URL company auth, track & task CRUD, template uploads
payments/        Razorpay order creation + server-side signature verification
certificates/    placeholder-substitution template engine, PDF rendering
templates/       all HTML templates, organised by app
static/css/      design system (styles.css)
media/templates/ company-uploaded certificate & offer-letter design folders
```

## How the certificate/offer-letter design system works

A company uploads a `.zip` (via the company portal → "Certificate design" /
"Offer letter design") containing:

```
index.html      # full design: HTML + <style> + <script>, all in one file
img/
  logo.png
  signature.png
  seal.png
  ...
```

`index.html` can use placeholders: `{{user_name}}`, `{{track_name}}`,
`{{college_name}}`, `{{degree}}`, `{{date}}`, `{{start_date}}`,
`{{certificate_id}}` (see `certificates/rendering.py` for the exact context
each document type gets). At render time the backend:

1. Loads `index.html` as **plain text** — it is never passed through Django's
   template engine, so it can't execute template tags or reach server data.
2. Substitutes `{{token}}` placeholders with HTML-escaped real values.
3. Rewrites `img/...` references to the uploaded folder's real media URL.
4. Serves the result as an HTML preview (dashboard iframe) or feeds it to
   WeasyPrint for a PDF download.

Uploads are extracted with path-traversal protection, a required-file check,
and a size cap (`MAX_TEMPLATE_ZIP_SIZE_MB`). A working example is already
seeded at `media/templates/certificate/default-seed/` and
`media/templates/offer_letter/default-seed/` — open `index.html` in either
folder to see the pattern.

## Security notes

- All secrets (Django secret key, Razorpay keys, DB/Redis URLs) come from
  environment variables — nothing sensitive is hard-coded.
- `DEBUG=False` automatically turns on HSTS, secure cookies, SSL redirect,
  and clickjacking protection (see the bottom of `config/settings.py`).
- The company portal lives behind an unlisted, configurable URL prefix and a
  `is_staff`-only check (`company/decorators.py`); there is no public
  registration path for it, matching the original brief.
- Login and registration POSTs are throttled per-IP by
  `core/middleware.py:RateLimitMiddleware` (10 attempts / 5 minutes,
  cache-backed so it works correctly once Redis is configured behind
  multiple app servers).
- Razorpay payments are verified **server-side** by recomputing the HMAC
  signature (`payments/views.py:verify_payment`) — the client's "success"
  callback is never trusted alone.
- Certificate access is gated by `has_paid`, checked fresh on every request —
  never inferred from client state.
- Uploaded certificate/offer-letter HTML is treated as a design asset, not
  code (see above) — this is the main defence against a malicious upload.

## Scaling this beyond a single server

- Set `DATABASE_URL` to point at Postgres — no model changes needed.
- Set `REDIS_URL` to move sessions, cache, and rate-limiting off individual
  app servers.
- `whitenoise` serves compressed, hashed static files without a separate
  static file server; for heavy media (uploaded template packages, generated
  PDFs) consider moving `MEDIA_ROOT` to S3-compatible object storage as
  traffic grows — the code only assumes `django.core.files.storage`, so this
  is a `STORAGES["default"]` change, not a rewrite.
- WeasyPrint PDF generation is CPU-bound; under real load, move certificate
  generation to a background worker (Celery/RQ) and let the download view
  poll or redirect once the file is ready, rather than generating inline on
  the request/response cycle.
- Run behind gunicorn/uvicorn + nginx in production — `manage.py runserver`
  is dev-only, as Django itself warns.

## What's stubbed / needs your input

- **Razorpay keys** — set `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in `.env`.
  Until they're set, the "Pay & Unlock Certificate" button returns a clear
  503 rather than silently failing.
- **Real certificate/offer-letter branding** — the seeded default design is a
  working placeholder; swap it via the company portal's upload flow.
- **Production secret key, allowed hosts, and CSRF trusted origins** — set in
  `.env` before deploying.
