# CivicConnect – Collaborative Societal Problem-Solving Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B%20%2F%206.x-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-brightgreen.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)](https://www.chartjs.org/)

**CivicConnect** is a responsive, full-stack web application built with **Python & Django** that crowdsources real-world societal challenges and facilitates collaborative problem-solving across citizens, students, universities, and industries.

---

## 1. Platform Overview

CivicConnect connects four key stakeholders into an active problem-solving network:
- **Citizens & Students:** Identify and submit societal challenges with interactive map pinpoints, propose actionable solutions, vote, join multidisciplinary project teams, and earn points on the Contributor Leaderboard.
- **Universities:** Publish academic and research challenges, discover student innovations, mentor collaborative projects, and partner with industry.
- **Industries:** Browse challenges and vetted solutions, sponsor projects as **Pilots**, propose strategic partnerships, and mentor student teams.
- **Platform Administrators:** Review and moderate challenges via POST-only moderation, verify university and industry organizations, monitor platform statistics, and access Django Admin.

---

## 2. Key Modules & Features

### Authentication & Role-Based Access (`accounts`)
- Custom User Model (`accounts.CustomUser`) supporting four roles: `student`, `university`, `industry`, `admin`.
- **Public Registration Control:** Registration is restricted to `student`, `university`, or `industry`. Admin accounts cannot be created via public registration.
- **Organization Verification (`is_verified`):** Students and administrators auto-verify on creation. University and industry partners default to unverified and require admin review before sending partnership requests or sponsoring pilots.
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
- **Industry Pilot Sponsorship:** Verified industry partners can sponsor an active project as a **Pilot**, displaying their sponsor badge on the project page.

### Partnerships & Directory (`partnerships`)
- Searchable partner directory of verified Academic Institutions and Industry Leaders.
- Formal collaboration proposals (`Mentorship`, `Technical R&D`, `Sponsorship`, `Student Placement`, `Strategic Partnership`).
- Incoming and outgoing proposal management with acceptance and response notes.

### Analytics Dashboard (`dashboard`)
- Accessible to administrators and verified university/industry partners at `/dashboard/analytics/`.
- Interactive Chart.js charts:
  1. Challenges by Category (Bar chart)
  2. Challenges by Status (Doughnut chart)
  3. Top Locations by Challenge Count (Horizontal bar chart)
  4. Solutions per Challenge (Top 10 bar chart)
  5. Platform summary metrics

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
├── partnerships/               # University & Industry Engagement
│   ├── models.py               # PartnershipRequest Model
│   ├── forms.py                # PartnershipRequestForm, ResponseForm
│   ├── views.py                # Directory, Proposals, Inbox/Outbox
│   └── urls.py                 # Partnership URLs
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
│   ├── partnerships/           # Directory, Proposal Form, Inbox
│   └── dashboard/              # Student, University, Industry, Admin, Analytics, Leaderboard
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

Running `python manage.py populate_db` seeds the following test accounts:

| Role | Username | Password | Organization / Description |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Platform Administrator |
| **University** | `univ_mit` | `mit123` | MIT Innovation Lab |
| **University** | `univ_stanford` | `stanford123` | Stanford Center for Social Impact |
| **University** | `univ_iit` | `iit123` | IIT Bombay CTARA |
| **Industry** | `ind_greenpower` | `green123` | GreenPower Energy Systems |
| **Industry** | `ind_techcorp` | `tech123` | Apex Technologies Global |
| **Student** | `student_alex` | `alex123` | Alex Chen |
| **Student** | `student_priya` | `priya123` | Priya Sharma |

---

## 7. Running Automated Tests

Run the test suite with:
```bash
python manage.py test
```
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
