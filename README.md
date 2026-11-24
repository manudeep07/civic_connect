# CivicConnect – Collaborative Societal Problem-Solving Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B%20%2F%206.x-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-brightgreen.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)](https://www.chartjs.org/)

**CivicConnect** is a responsive, full-stack web application built with **Python & Django** that crowdsources real-world societal challenges and facilitates collaborative problem-solving across citizens, students, universities, and industries.

---

## 1. Platform Overview

CivicConnect connects stakeholders into an active problem-solving network:
- **Citizens & Students:** Identify and submit societal challenges with interactive map pinpoints, propose actionable solutions, vote, join multidisciplinary project teams, and earn points on the Contributor Leaderboard.
- **Organizations (Universities, Industry, Government & NGOs):** Publish challenges, discover student innovations, mentor collaborative projects, and sponsor projects as **Pilots**.
- **Platform Administrators:** Review and moderate challenges via POST-only moderation, verify organizations, monitor platform statistics, and access Django Admin.

---

## 2. Key Modules & Features

### Authentication & Role-Based Access (`accounts`)
- Custom User Model (`accounts.CustomUser`) supporting simplified roles: `citizen` (Citizen / Student), `organization` (University, Industry, Government / NGO), and `admin`.
- **Organization Type (`org_type`):** Applicable when role is `organization`, choosing between `university`, `industry`, or `government_ngo`.
- **Public Registration Control:** Public registration is available for `citizen` and `organization`. Admin accounts cannot be created via public registration.
- **Organization Verification (`is_verified`):** Citizens and administrators auto-verify on creation. Organizations default to unverified (`is_verified=False`) and require admin review before they can post official responses, submit solutions as an organization, lead projects, or sponsor pilots.
- **Security & Integrity:** Image file validation (JPEG/PNG/WEBP, max 2 MB), safe host redirection, POST-only logout, and 8-character minimum passwords.

### Challenge Management (`challenges`)
- Fields: Title, Category, Location, Coordinates (Latitude & Longitude), Severity (Low, Medium, High, Critical), Expected Impact, Image (optional), Affiliated Organization.
- Workflow: `Pending` &rarr; `Approved` &rarr; `In Progress` &rarr; `Solved` (plus `Rejected`).
- **Interactive Map Picker:** Set location via Leaflet map click, draggable pin, "Use my current location", or debounced Nominatim browser search.
- **Geospatial Map (`/challenges/map/`):** Full-screen Leaflet view with marker clustering (`Leaflet.markercluster`), severity color-coding, filters by category/severity/status, and safe DOM popup rendering.
- **Detail View Map:** Challenges with pinned coordinates display a compact, read-only location map.
- **Moderation Reversion:** If a non-admin creator edits an approved challenge, it automatically reverts to `pending` review.

### Solutions & Collaborative Projects (`solutions`, `collaborations`)
- **Proposals:** Detailed technical solutions with milestones, duration, and required resources.
- **Acceptance:** Challenge creators or administrators can accept proposals. Acceptance allows launching a project workspace.
- **Workspaces:** Real-time milestone progress tracking ($0\% - 100\%$), status management (`Planning`, `Active`, `Pilot`, `On Hold`, `Completed`), and team role assignment.
- **Pilot Sponsorship:** Verified organizations can sponsor an active project as a **Pilot**, displaying their sponsor badge on the project page.

### Dashboards & Analytics (`dashboard`)
- **Citizen Dashboard:** Tracks personal challenges, proposed solutions, collaborative project memberships, and votes.
- **Organization Dashboard:** Unified workspace displaying assigned/published challenges, solutions, sponsored pilots, and active collaborations.
- **Admin Dashboard:** Moderation queue for challenges, user management, and system overview.
- **Analytics Dashboard:** Accessible to administrators and verified organizations at `/dashboard/analytics/` with interactive Chart.js charts.

### Contributor Leaderboard (`dashboard`)
- Accessible at `/dashboard/leaderboard/`.
- Points awarded via `accounts.models.UserScore`:
  - **Submit a Challenge:** +10 points
  - **Solution Accepted:** +25 points
  - **Project Completed:** +50 points
- Ranks top contributors with medals (🥇, 🥈, 🥉), role badges, and displays the user's score.

---

## 3. Technology Stack & Architecture

- **Backend:** Python 3, Django (MVT pattern)
- **Database:** SQLite (local development); PostgreSQL via `DATABASE_URL` (production)
- **WSGI Server:** Gunicorn
- **Static Assets:** WhiteNoise (`whitenoise.storage.CompressedManifestStaticFilesStorage`) configured through Django's `STORAGES` dictionary
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Visualizations:** Chart.js 4.4, Leaflet.js 1.9.4, Leaflet.markercluster 1.5.3

### Frontend Design System

CivicConnect uses a **token-based design system** (`static/css/style.css`) inspired by Linear and Stripe docs — calm, minimal, trustworthy.

**Design tokens (`:root` CSS variables):**
| Token | Value | Usage |
|---|---|---|
| `--civic-bg` | `#ffffff` | Page background |
| `--civic-surface` | `#f8fafc` | Card/section surfaces |
| `--civic-text` | `#0f172a` | Primary text |
| `--civic-text-muted` | `#64748b` | Secondary text |
| `--civic-border` | `#e2e8f0` | Borders |
| `--civic-accent` | `#2563eb` | Single accent (buttons, links) |
| `--civic-accent-hover` | `#1d4ed8` | Accent hover state |

**Rules:** 0 `linear-gradient`, 0 `radial-gradient`, 0 `backdrop-filter`, 0 `translateY` hover lifts. Max 5 inline `style=` attributes in all templates (only dynamic progress bar widths).

### Leaflet (Vendored Locally)

Leaflet 1.9.4 and Leaflet.markercluster 1.5.3 are **vendored locally** (no CDN dependency):
- CSS/JS: `static/vendor/leaflet/` and `static/vendor/markercluster/`
- Marker images: `static/vendor/leaflet/images/`
- Loaded via `templates/partials/leaflet_assets.html` using `{% static %}` tags

`SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'` is set in `settings.py` so tile servers receive a valid Referer header (fixes grey tiles on some browsers).

---

## 4. Project Directory Structure

```
civicconnect/
├── manage.py
├── requirements.txt
├── Procfile
├── build.sh
├── .env.example
├── README.md
├── db.sqlite3
│
├── civicconnect/               # Project Root Configuration
│   ├── settings.py             # Settings, Database, Auth & Storages
│   ├── urls.py                 # Master URL Router
│   ├── views.py                # Home Landing Page & About View
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   # Authentication & User Management
│   ├── models.py               # CustomUser, Activity, UserScore
│   ├── forms.py                # Registration, Login, Profile Forms
│   ├── validators.py           # Image validation (size, MIME type)
│   ├── views.py                # Auth, Profile, Password Views
│   ├── urls.py                 # Account URLs
│   ├── admin.py                # User admin with verification actions
│   └── context_processors.py   # Global role flags processor
│
├── challenges/                 # Challenges, Voting & Comments
│   ├── models.py               # Category, Challenge, Vote, Comment
│   ├── forms.py                # ChallengeForm (with map coordinates), CommentForm
│   ├── views.py                # Browse, Search, Detail, Vote, Comment, Map View
│   ├── urls.py                 # Challenge URLs
│   ├── tests.py                # Comprehensive Automated Test Suite
│   └── management/commands/
│       ├── populate_db.py      # Seed Script with Hardcoded Coordinates
│       └── geocode_challenges.py # Backfill Command for Missing Coordinates
│
├── solutions/                  # Solution Management
│   ├── models.py               # Solution Model
│   ├── forms.py                # SolutionForm
│   ├── views.py                # Submit, Review, Accept Toggle
│   └── urls.py                 # Solution URLs
│
├── collaborations/             # Projects & Team Workspaces
│   ├── models.py               # Project (with Pilot status), ProjectMembership
│   ├── forms.py                # ProjectForm, MembershipAddForm
│   ├── views.py                # Workspace, Member Management, Pilot Sponsorship
│   └── urls.py                 # Collaboration URLs
│
├── dashboard/                  # Dashboards, Analytics & Leaderboard
│   ├── views.py                # Role Dashboards, Analytics, Leaderboard
│   └── urls.py                 # Dashboard URLs
│
├── templates/                  # Django HTML Templates
│   ├── base.html               # Master Layout & Navbar
│   ├── home.html               # Landing Page with Pulse Metrics
│   ├── about.html              # About Platform Overview, Workflow & FAQ
│   ├── accounts/               # Login, Register, Profile, Passwords
│   ├── challenges/             # List, Detail, Form, Map View
│   ├── solutions/              # Form, Detail, Confirm Delete
│   ├── collaborations/         # Project List, Workspace, Form
│   └── dashboard/              # Student/Citizen, Organization, Admin, Analytics, Leaderboard
│
└── static/                     # Static Assets (CSS, JS)
```

---

## 5. Local Setup Instructions

### Step 1: Clone or Navigate to the Repository
```bash
cd e:\django-project
```

### Step 2: Create and Activate Virtual Environment
**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```
Default `.env` configuration for local development:
```ini
SECRET_KEY=django-insecure-local-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

### Step 5: Run Database Migrations
```bash
python manage.py migrate
```

### Step 6: Seed Database
```bash
python manage.py populate_db
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 6. Demo Accounts

Running `python manage.py populate_db` seeds the following demo accounts (1 admin, 3 organizations across all org types, and 2 citizens):

| Role | Organization Type | Username | Password | Organization / Description |
|---|---|---|---|---|
| **Administrator** | — | `admin` | `admin123` | Platform Superuser & Administrator |
| **Organization** | `university` | `univ_mit` | `mit123` | MIT Innovation Lab |
| **Organization** | `industry` | `ind_greenpower` | `green123` | GreenPower Energy Systems |
| **Organization** | `government_ngo` | `ngo_baykeeper` | `bay123` | Tampa Bay Baykeeper NGO |
| **Citizen / Student** | — | `student_alex` | `alex123` | Alex Chen (Citizen Innovator) |
| **Citizen / Student** | — | `student_priya` | `priya123` | Priya Sharma (Citizen Researcher) |

---

## 7. Running Automated Tests

Run the test suite with:
```bash
python manage.py test
```

> **Note:** `python manage.py test` works with no `.env` file or environment variables set (test runs automatically use a safe throwaway test key and skip HTTPS/SSL redirects). Copying the environment template (`cp .env.example .env`) is needed only for `runserver`.

The test suite covers:
- Registration rejection of administrative role
- Role auto-verification logic (students vs organizations)
- Challenge permissions (creator edit/delete, non-owner restrictions)
- Reversion of edited approved challenges to pending review
- Voting toggles, POST-only enforcement, and status guards
- Comment creation, deletion, and status guards
- Solution submission guards and acceptance toggling
- Collaborative project creation guards from accepted solutions
- Industry pilot sponsorship workflow
- Partnership request verification restrictions and response flows
- Coordinate validation (bounds, paired coordinates)
- Geospatial map view output and XSS script tag escaping
- Smoke tests requesting every GET page across all user roles
- Regression tests for challenge detail with/without accepted solution

---

## 8. Deployment on Render

CivicConnect includes `Procfile`, `build.sh`, WhiteNoise static file compression, and PostgreSQL database support via `DATABASE_URL`.

### Step 1: Create PostgreSQL Database on Render
1. Log in to [Render](https://render.com).
2. Click **New +** &rarr; **PostgreSQL**.
3. Name your database (e.g., `civicconnect-db`).
4. Copy the **Internal Database URL** (or External URL).

### Step 2: Create Web Service on Render
1. Click **New +** &rarr; **Web Service**.
2. Connect your Git repository.
3. Configure settings:
   - **Name:** `civicconnect`
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn civicconnect.wsgi:application`

### Step 3: Set Environment Variables
Under the **Environment** tab, set:
- `SECRET_KEY`: A secure random secret string (e.g. 50+ characters).
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`
- `DATABASE_URL`: The PostgreSQL connection URL from Step 1.
- `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.onrender.com`

### Step 4: Seed Initial Data (Optional)
Open the **Shell** tab in your Render dashboard and run:
```bash
python manage.py populate_db
```
Or create a custom administrator:
```bash
python manage.py createsuperuser
```
