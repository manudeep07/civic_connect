# CivicConnect – Collaborative Societal Problem-Solving Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B%20%2F%206.x-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-brightgreen.svg)](https://leafletjs.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange.svg)](https://www.chartjs.org/)
[![INT253](https://img.shields.io/badge/Academic-INT253%20Capstone-navy.svg)](#course-outcomes-int253)

**CivicConnect** is a responsive, full-stack web application built with **Python & Django** that crowdsources real-world societal challenges and facilitates collaborative problem-solving across citizens, students, universities, and industries.

---

## 1. Platform Overview

CivicConnect connects four key stakeholders:
- **Citizens & Students:** Identify and submit societal challenges, propose solutions, vote, join project teams, and earn points on the leaderboard.
- **Universities:** Publish academic and research challenges, discover student innovations, mentor collaborative projects, and partner with industry.
- **Industries:** Browse challenges and solutions, sponsor projects as **Pilots**, propose partnerships, and mentor student teams.
- **Platform Administrators:** Review and moderate challenges via POST-only moderation, verify university and industry organizations, monitor platform statistics, and access Django Admin.

---

## 2. Technology Stack & Architecture

- **Backend:** Python 3, Django (MVT architecture)
- **Database:** SQLite for local development; PostgreSQL via `DATABASE_URL` (using `dj-database-url` and `psycopg2-binary`) for production
- **Static Assets:** WhiteNoise (`whitenoise.storage.CompressedManifestStaticFilesStorage`)
- **WSGI Server:** Gunicorn
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Interactive Visualizations:** Chart.js 4.4 (Analytics), Leaflet.js 1.9.4 & OpenStreetMap (Geospatial Challenge Map)
- **Configuration & Security:** Environment variables via `python-decouple` / `os.environ`, secure cookies on production (`DEBUG=False`), image validation (max 2 MB, JPG/PNG/WEBP), CSRF protection on all mutating actions, `@require_POST` guards, safe redirect host validation.

---

## 3. Implemented Modules & Features

### Authentication & Authorization (`accounts`)
- Custom User Model (`accounts.CustomUser`) with roles: `student`, `university`, `industry`, `admin`.
- **Public registration restriction:** Registration form allows only `student`, `university`, or `industry`. Admin accounts cannot be created via public registration.
- **Organization verification:** `is_verified` boolean field. Students and admins are auto-verified. University and industry partners default to unverified and must be verified by administrators before sending partnership requests or sponsoring pilots.
- **Image validation:** Uploaded avatars and challenge images are validated for allowed formats (JPEG, PNG, WEBP) and maximum size (2 MB).
- **Secure session & auth:** Open-redirect prevention using `url_has_allowed_host_and_scheme`, POST-only logout, password minimum length of 8 characters.

### Challenge Management (`challenges`)
- Fields: Title, Category, Location, Problem Severity (Low, Medium, High, Critical), Expected Impact, Image (optional), Affiliated Organization.
- Workflow: `Pending` &rarr; `Approved` &rarr; `In Progress` &rarr; `Solved` (plus `Rejected`).
- Only approved/in-progress/solved challenges are publicly visible. Pending challenges are visible only to their creator or administrators.
- **Moderation safety:** If a creator edits an approved challenge, it automatically reverts to `pending` review (unless edited by an administrator).
- **Leaflet Map View:** Geospatial map at `/challenges/map/` visualizing geocoded challenge coordinates with severity-coded pins.

### Community Engagement (`challenges`, `solutions`)
- **Upvoting:** One-vote-per-user enforced by database constraint. Voting is blocked on unapproved challenges. POST-only endpoint.
- **Comments:** Community feedback threads on approved challenges. Blocked on pending challenges. Users can delete their own comments.
- **Solutions:** Submitted by users on approved/in-progress challenges. Challenge creator or admin can toggle solution acceptance.

### Collaborative Projects (`collaborations`)
- Created from accepted solutions. Guarded: challenge must be approved, solution must be accepted, and user must be the solution creator or an admin.
- Project statuses: `Planning`, `Active`, `Pilot`, `On Hold`, `Completed`.
- **Industry Pilot Sponsorship:** Verified industry partners can sponsor an active project as a **Pilot** (`/collaborations/<id>/sponsor-pilot/`), displaying the sponsor badge on the project page.
- Project memberships and roles (e.g. Project Lead, Student Researcher, Faculty Mentor, Contributor). POST-only team join and member management.

### University & Industry Partnerships (`partnerships`)
- Partner directory with search and role filtering.
- Formal partnership requests (`mentorship`, `technical`, `sponsorship`, `student_internship`, `general_collaboration`).
- Restricted: unverified university/industry users cannot send partnership requests.
- Target organizations can accept or decline incoming requests with response notes.

### Analytics Dashboard (`dashboard`)
- Accessible to administrators and verified university/industry partners at `/dashboard/analytics/`.
- Interactive Chart.js charts:
  1. Challenges by Category (Bar chart)
  2. Challenges by Status (Doughnut chart)
  3. Top Locations by Challenge Count (Horizontal bar chart)
  4. Solutions per Challenge (Top 10 bar chart)
- Summary pulse metric cards.

### Contributor Leaderboard (`dashboard`)
- Accessible at `/dashboard/leaderboard/`.
- Point system tracked via `accounts.models.UserScore`:
  - **Submit a Challenge:** +10 points
  - **Solution Accepted:** +25 points
  - **Project Completed:** +50 points
- Ranks top contributors with medals (🥇, 🥈, 🥉), role badges, and displays the logged-in user's score.

---

## 4. Local Development Setup

### 1. Prerequisites
- Python 3.10+
- `pip` and virtual environment support

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone or navigate to the repository
cd e:\django-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows:
copy .env.example .env
# Linux / macOS:
cp .env.example .env
```
Default values in `.env`:
```ini
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
# Leave DATABASE_URL blank to use SQLite locally
```

### 4. Database Migrations & Seeding
```bash
python manage.py migrate
python manage.py populate_db
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/`.

---

## 5. Demo Accounts

Running `python manage.py populate_db` seeds the following test accounts:

| Role | Username | Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Superuser / staff |
| **University** | `univ_mit` | `mit123` | MIT Innovation Lab |
| **University** | `univ_stanford` | `stanford123` | Stanford Center for Social Impact |
| **Industry** | `ind_greenpower` | `green123` | GreenPower Energy |
| **Industry** | `ind_techcorp` | `tech123` | Apex Technologies |
| **Student** | `student_alex` | `alex123` | Alex Chen |
| **Student** | `student_priya` | `priya123` | Priya Sharma |

---

## 6. Automated Test Suite

Run the full test suite with:
```bash
python manage.py test
```
The test suite covers:
- Registration cannot create an admin account (`RegistrationTests`)
- Organization verification auto-logic (`RegistrationTests`)
- Permission checks on challenge edit & delete (`ChallengePermissionTests`)
- Reversion to pending when creator edits an approved challenge (`ChallengePermissionTests`)
- Admin moderation POST-only workflows (`AdminModerationTests`)
- Voting toggle and status guards (`VoteTests`)
- Commenting restrictions on pending challenges (`CommentTests`)
- Solution submission guards and acceptance workflow (`SolutionTests`)
- Project creation permissions and accepted-solution requirement (`ProjectTests`)
- Partnership request verification checks and response flow (`PartnershipTests`)
- Analytics access permissions (`AnalyticsTests`)
- Industry pilot sponsorship workflow (`PilotSponsorTests`)
- Leaderboard point awards (`LeaderboardTests`)
- Leaflet map view rendering (`MapViewTests`)

---

## 7. Deployment Instructions (Render)

CivicConnect is production-ready for deployment on [Render](https://render.com) using PostgreSQL, Gunicorn, and WhiteNoise.

### Step 1: Create a PostgreSQL Database on Render
1. Log in to your Render Dashboard.
2. Click **New +** &rarr; **PostgreSQL**.
3. Name your database (e.g. `civicconnect-db`).
4. Select the Free tier and click **Create Database**.
5. Once created, copy the **Internal Database URL** (or External URL if deploying from outside Render).

### Step 2: Create a Web Service on Render
1. In Render Dashboard, click **New +** &rarr; **Web Service**.
2. Connect your Git repository.
3. Configure the service:
   - **Name:** `civicconnect`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Build Command:** `./build.sh` (or `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`)
   - **Start Command:** `gunicorn civicconnect.wsgi:application`

### Step 3: Configure Environment Variables
Under the **Environment** tab of your Render Web Service, add:
- `SECRET_KEY`: A secure random 50+ character string.
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`
- `DATABASE_URL`: Paste the PostgreSQL URL from Step 1.
- `PYTHON_VERSION`: `3.11.9` (or your Python version)

### Step 4: Seed Data (Optional)
In the Render Web Service dashboard, open the **Shell** tab and run:
```bash
python manage.py populate_db
```
Or create a custom superuser:
```bash
python manage.py createsuperuser
```

WhiteNoise will automatically serve compressed static files with cache headers, and Gunicorn will handle concurrent HTTP requests.

---

## 8. Course Outcomes (INT253)

| Outcome | Syllabus Topic | Implementation in CivicConnect |
|---|---|---|
| **CO1** | Modular Django App Structure | 6 decoupled applications (`accounts`, `challenges`, `solutions`, `collaborations`, `partnerships`, `dashboard`). |
| **CO2** | Views, URL Routing & HTTP Methods | RESTful GET/POST views, `@require_POST`, paginated listings, search filters, geocoding. |
| **CO3** | Templates & Context Processors | Bootstrap 5 UI, template inheritance (`base.html`), role-based navigation context processor. |
| **CO4** | Django Forms & Validation | ModelForms with custom validators (file size, image type, min password length). |
| **CO5** | Models, ORM & Aggregations | Relational schemas, `UniqueConstraint`, `ForeignKey` cascades, dynamic `Count`/`Sum` aggregations. |
| **CO6** | Security, Sessions & Auth | PBKDF2 hashing, secure cookie flags, CSRF tokens, open-redirect prevention, role-based decorators. |
