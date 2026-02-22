# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TuitionHub is a Django-based CS tutoring platform for booking sessions and processing payments. It supports one-to-one and group sessions (up to 3 students), online and face-to-face delivery, with SumUp payment integration.

## Development Commands

```bash
# Activate virtualenv first
source venv/bin/activate

# Setup and run
python manage.py migrate
python manage.py setup_initial_data           # Create time slots and configure Site
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py createsuperuser              # Uses email (no username)

# Production
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

No test suite or linter is configured. Test files exist but are empty stubs.

## Architecture

### Apps and URL Namespaces

| App | Namespace | URL Prefix | Purpose |
|-----|-----------|------------|---------|
| core | `core` | `/` | Public pages (home, about, pricing, contact) |
| core | `dashboard` | `/dashboard/` | Authenticated user views (via `core/urls_dashboard.py`) |
| courses | `courses` | `/courses/` | Course catalog and enrollment |
| bookings | `bookings` | `/bookings/` | Session booking, calendar, availability API |
| payments | `payments` | `/payments/` | SumUp checkout, webhooks, invoices |
| allauth | `account_*` | `/accounts/` | Authentication (email-based, no username) |

Note: The `dashboard` namespace is **not** a separate app — it's a second URL module in the `core` app (`core/urls_dashboard.py`).

### Key Patterns

**Custom User Model** (`core.User`): Email is `USERNAME_FIELD`, no username field at all. `REQUIRED_FIELDS = ['first_name', 'last_name']`. Roles: STUDENT (default), TUTOR, ADMIN. Uses allauth with the newer settings format (v0.56+):
- `ACCOUNT_LOGIN_METHODS = {'email'}`
- `ACCOUNT_USER_MODEL_USERNAME_FIELD = None`

**Monetary Values**: All prices stored in **pence** (integers) to avoid floating-point issues. Models expose `price_display` / `amount_display` properties returning formatted strings like `"£60.00"`. The `PRICING` dict in `config/settings.py` is also in pence.

**Booking → Payment Flow**: `BookingForm` saves with `commit=False`, sets `end_time` and `price` via `calculate_price()`, then redirects to `payments:checkout`. The checkout view creates a `Payment` record and initiates SumUp. The `BookingForm.__init__` takes a `user` keyword argument.

**SumUp Service** (`payments/services.py`): Returns mock data in demo mode when `SUMUP_API_KEY` is empty. Demo checkout IDs are prefixed with `demo-`.

**Context Processor** (`core/context_processors.py`): Injects `SITE_NAME`, `SITE_TAGLINE`, `TUTOR_NAME`, `PRICING` (in pounds, not pence), `CONTACT_EMAIL`, `CONTACT_PHONE`, and `DEBUG` into all templates.

### Frontend Stack

- **Tailwind CSS** via CDN (`<script src="https://cdn.tailwindcss.com">`) with custom `primary`/`secondary` color palette configured in `base.html`
- **HTMX** for dynamic UI (e.g., `bookings/api/slots/` endpoint returns available slots)
- **Alpine.js** for client-side interactions (mobile menu, dismissible messages)
- Custom CSS utility classes defined in `base.html`: `.form-input`, `.form-textarea`, `.form-select`, `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-outline`
- Templates live in the project-level `templates/` directory, organized by app name

### Course Content Hierarchy

Level → Subject → Course → Topic → Lesson → Resource, with `StudentProgress` tracking per user/lesson. Courses use `is_published` and `is_featured` flags for visibility.

## Configuration

Environment variables via `.env` (see `.env.example`):
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- `DATABASE_URL` (optional, defaults to SQLite)
- `RESEND_API_KEY`, `DEFAULT_FROM_EMAIL` (email via `core/email_backend.py`; console backend in DEBUG)
- `SUMUP_API_KEY`, `SUMUP_MERCHANT_CODE` (payments; empty = demo mode)
- `PAYMENTS_ENABLED` (default `False`; when `False`, bookings auto-confirm without payment, payment URLs return 404, and all payment UI is hidden; pricing info stays visible)

Locale: `en-gb`, timezone: `Europe/London`.
