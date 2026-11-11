# CivicConnect – Collaborative Societal Problem-Solving Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1%2F5.0%2B-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![INT253](https://img.shields.io/badge/Academic-INT253%20Capstone-navy.svg)](#8-django-concepts--int253-course-outcome-mapping)

**CivicConnect** is a responsive, full-stack web application built with **Python & Django** that crowdsources real-world societal challenges and facilitates collaborative problem-solving across citizens, students, universities, and industries.

---

## 1. Platform Overview & Architecture

CivicConnect bridges the gap between community issues and technical execution:
- **Citizens & Students** identify and report authentic societal challenges, propose innovations, and join interdisciplinary project teams.
- **Universities** publish research challenges, discover promising student innovations, assign faculty mentors, and provide laboratory infrastructure.
- **Industries & Corporations** discover validated solutions, sponsor capstone hardware, provide technical mentorship, and run commercial pilots.
- **Platform Administrators** monitor the platform, review submitted challenges, manage categories, and oversee collaborations.

---

## 2. Technology Stack

- **Backend:** Python 3, Django 6.x / 5.x
- **Architecture Pattern:** Model-View-Template (MVT)
- **Database:** SQLite (for easy local setup and zero-config deployment)
- **Frontend:** HTML5, CSS3, Modern JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Security & Forms:** Django Forms, CSRF Protection, PBKDF2 Password Hashing, Session Authentication, Messages Framework

---

## 3. Key Modules and Features

### Module 1: Authentication & Role-Based Access Control
- Custom User Model (`accounts.CustomUser`) with 4 distinct roles:
  1. `student` (Citizen / Student)
  2. `university` (University / Academic Institution)
  3. `industry` (Industry / Corporate Partner)
  4. `admin` (Platform Administrator)
- User registration with role selection, organization/institution affiliation, and location.
- Secure login, logout, and profile management with avatar upload and biography.
- Password change and Django-powered password reset workflow.

### Module 2: Interactive Landing Page
- High-impact hero section with platform pulse metrics.
- Multi-stakeholder workflow visualization (Crowdsource &rarr; Propose &rarr; Mentor &rarr; Track Impact).
- Featured challenges grid with real-time upvote and solution counts.
- Dynamic platform statistics fetched directly from the database.
- University & Industry partner showcases.

### Module 3: Challenge Management
- Challenge submission with Title, Category, Location, Problem Severity (Low, Medium, High, Critical), Expected Impact, and Image upload.
- Categorization across 9 critical domains (Environment, Education, Healthcare, Agriculture, Transportation, Public Safety, Waste Management, Rural Development, Technology & Innovation).
- Challenge workflow: `Pending` &rarr; `Approved` &rarr; `In Progress` &rarr; `Solved`.
- Multi-criteria search, category filters, severity filters, sorting (Latest, Most Upvoted, Most Solutions), and pagination (6 items/page).
- Only approved challenges are publicly visible; pending challenges undergo administrative review.

### Module 4: Community Voting & Discussion
- One-vote-per-user restriction enforced via database `UniqueConstraint`.
- Live upvote toggle with instant state reflection.
- Threaded community discussion with author role badges, timestamps, and user comment deletion.

### Module 5: Solution Management
- Detailed technical proposals with implementation roadmaps, duration, expected outcomes, and resource requirements.
- Challenge creators and administrators can accept solutions.
- Acceptance triggers collaborative project launch capabilities.

### Module 6: Collaborative Projects & Team Management
- Transform accepted solutions into multi-disciplinary project workspaces.
- Real-time milestone and completion progress tracking ($0\% - 100\%$).
- Interdisciplinary team management: Project Leads can invite registered users and assign specialized roles (e.g., *Student Developer*, *Faculty Mentor*, *Industry Advisor*).
- One-click "Join Project Team" for students and community members.

### Module 7: University & Industry Partnerships
- Verified directory of Academic Institutions and Industry Organizations.
- Formal collaboration proposals specifying partnership scopes (*Mentorship*, *Technical R&D*, *Sponsorship*, *Student Placement*).
- Incoming and outgoing proposal management with acceptance and response notes.

### Module 8: Role-Specific Dashboards
Dynamic, database-driven metrics and dashboards tailored to each stakeholder:
- **Citizen / Student:** My Challenges, My Solutions, My Project Teams, My Votes, Activity stream.
- **University:** Published Academic Challenges, Associated Research Projects, Student Solutions for Review, Pending Partnership Inquiries.
- **Industry:** Urgent Challenges for Co-Sponsorship, Active Collaborations, Sent & Received Partnership Requests.
- **Administrator:** Platform-wide stats, **1-Click Challenge Moderation (Approve/Reject)**, Recent Registrations, and Direct Django Admin shortcuts.

---

## 4. Django Concepts – INT253 Course Outcome Mapping

| Outcome | Syllabus Topic | Implementation in CivicConnect |
|---|---|---|
| **CO1** | Installation, Project Creation & Modular App Structuring | Clean settings configuration; modular decomposition into 6 independent apps (`accounts`, `challenges`, `solutions`, `collaborations`, `partnerships`, `dashboard`). |
| **CO2** | Views, URL Mapping & HTTP Methods | App-level URL namespacing; RESTful GET/POST workflows; multi-parameter search/filter querying; pagination with `django.core.paginator.Paginator`. |
| **CO3** | Django Templates & Context Processors | Base layout inheritance (`base.html`), template filters, tags, and custom context processor (`user_roles_processor`) dynamically injecting role permissions. |
| **CO4** | Django Forms & Input Validation | ModelForms (`UserRegistrationForm`, `ChallengeForm`, `SolutionForm`, `ProjectForm`, `PartnershipRequestForm`), CSRF protection, and custom `clean()` validation. |
| **CO5** | Models, ORM, Migrations & Admin | 10 relational models with `ForeignKey`, `OneToOneField`, `UniqueConstraint`, ORM queries, aggregations (`Count`), and custom Django Admin actions (*Batch Approve*, *Batch Reject*). |
| **CO6** | Cookies, Sessions & Authentication | Session-based authentication, PBKDF2 password hashing, role-based view decorators (`@login_required`, `@role_required`), and flash alerts via the Django Messages Framework. |

---

## 5. Project Directory Structure

```
django-project/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
│
├── civicconnect/               # Project Root Configuration
│   ├── settings.py             # Settings, Database, Auth & Context Processors
│   ├── urls.py                 # Master URL Router & Static Routing
│   ├── views.py                # Home Landing Page & About View
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   # Module 1: Auth & User Management
│   ├── models.py               # CustomUser & Activity Models
│   ├── forms.py                # Registration, Login, Profile Forms
│   ├── views.py                # Auth, Profile, Password Views
│   ├── urls.py                 # Accounts Routing
│   ├── admin.py                # CustomUserAdmin
│   ├── context_processors.py   # Role Helper Context Processor
│   └── utils.py                # Activity Logger & Role Decorator
│
├── challenges/                 # Module 3 & 4: Challenges, Voting & Comments
│   ├── models.py               # Category, Challenge, Vote, Comment
│   ├── forms.py                # ChallengeForm, CommentForm
│   ├── views.py                # Browse, Search, Detail, Vote, Comment
│   ├── urls.py                 # Challenge URLs
│   ├── admin.py                # Admin with 1-Click Batch Actions
│   ├── tests.py                # Full Automated Test Suite
│   └── management/commands/
│       └── populate_db.py      # Seed Script with Demo Data
│
├── solutions/                  # Module 5: Solution Management
│   ├── models.py               # Solution Model
│   ├── forms.py                # SolutionForm
│   ├── views.py                # Submit, Review, Accept Toggle
│   ├── urls.py                 # Solution URLs
│   └── admin.py                # Solution Admin
│
├── collaborations/             # Module 6: Projects & Team Workspaces
│   ├── models.py               # Project, ProjectMembership
│   ├── forms.py                # ProjectForm, ProjectMembershipAddForm
│   ├── views.py                # Project List, Workspace, Member Management
│   ├── urls.py                 # Collaboration URLs
│   └── admin.py                # Project Admin with Inlines
│
├── partnerships/               # Module 7: University & Industry Engagement
│   ├── models.py               # PartnershipRequest Model
│   ├── forms.py                # PartnershipRequestForm, ResponseForm
│   ├── views.py                # Directory, Send Proposal, Inbox/Outbox
│   ├── urls.py                 # Partnership URLs
│   └── admin.py                # Partnership Admin
│
├── dashboard/                  # Module 8: Role-Specific Dashboards
│   ├── views.py                # Dynamic Student, University, Industry & Admin Views
│   └── urls.py                 # Dashboard Routing & 1-Click Moderation
│
├── templates/                  # Django HTML Templates
│   ├── base.html               # Master Layout & Navbar
│   ├── home.html               # Landing Page with Pulse Metrics
│   ├── about.html              # INT253 Course Outcomes Mapping
│   ├── accounts/               # Login, Register, Profile, Passwords
│   ├── challenges/             # List, Detail, Form, Confirm Delete
│   ├── solutions/              # Form, Detail, Confirm Delete
│   ├── collaborations/         # Project List, Workspace, Form
│   ├── partnerships/           # Directory, Proposal Form, Inbox
│   └── dashboard/              # Student, University, Industry, Admin
│
├── static/                     # Static Assets
│   ├── css/style.css           # Custom CivicConnect Design System
│   └── js/script.js            # Auto-Alerts, Counters, Tooltips
└── media/                      # Uploaded Challenge Photos & Avatars
```

---

## 6. Installation & Local Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14+
- `pip` (Python package manager)
- Git (optional)

### Step 1: Clone or Navigate to the Project Directory
```bash
cd e:\django-project
```

### Step 2: Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```
**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Seed Demo Data (Recommended)
CivicConnect includes a pre-built database seeding command that creates realistic categories, users across all 4 roles, societal challenges, accepted solutions, collaborative project teams, and partnership requests:
```bash
python manage.py populate_db
```

### Step 6: Create an Additional Superuser (Optional)
If you wish to create a custom administrative user manually:
```bash
python manage.py createsuperuser
```

### Step 7: Run the Development Server
```bash
python manage.py runserver
```
Open your browser and navigate to:
**http://127.0.0.1:8000/**

---

## 7. Demo Accounts & Pre-Configured Credentials

When you run `python manage.py populate_db`, the following accounts are available for testing:

| Role | Username | Password | Organization / Description |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | Platform Chief Administrator (Django Admin & 1-Click Moderation) |
| **University** | `univ_mit` | `mit123` | MIT Innovation Lab |
| **University** | `univ_stanford` | `stanford123` | Stanford Center for Social Impact |
| **University** | `univ_iit` | `iit123` | IIT Bombay Rural Technology Cell |
| **Industry** | `ind_greenpower` | `green123` | GreenPower Energy Solutions (CSR & Renewable Tech) |
| **Industry** | `ind_techcorp` | `tech123` | Apex Technologies Global (AI & Robotics R&D) |
| **Industry** | `ind_agrisolutions` | `agri123` | AgriGrow Sustainable Hardware |
| **Student / Citizen** | `student_alex` | `alex123` | Alex Chen (Mechanical Engineering Student & Project Lead) |
| **Student / Citizen** | `student_priya` | `priya123` | Priya Sharma (Computer Science AI Researcher & Project Lead) |
| **Student / Citizen** | `citizen_john` | `john123` | John Miller (Community Environmental Advocate) |
| **Student / Citizen** | `citizen_fatima` | `fatima123` | Fatima Al-Hassan (Rural Healthcare Nurse Volunteer) |

---

## 8. Running Automated Tests

CivicConnect includes automated test coverage validating end-to-end functionality:
```bash
python manage.py test
```
The test suite validates:
1. Landing page rendering and statistics.
2. Challenge submission, review states, and 1-click administrative approval.
3. Upvoting and comment creation/deletion.
4. Solution submission, owner acceptance, and project workspace launch.
5. Partnership request transmission and response.
6. Role-specific dashboard rendering across all 4 roles.

---

## 9. License & Academic Attribution
Developed as part of the **INT253: Web Development using Python / Django** curriculum. Designed for academic demonstration of full-stack Django architecture, multi-role access control, and civic technology.

