# College Placement Manager — Functional & Non-Functional Requirements

## 1. Overview
The **College Placement Manager** is a specialized campus hiring platform designed to streamline, automate, and bring complete transparency to the campus recruitment lifecycle. It bridges Placement Officers, Students, and Corporate Recruiters under an integrated, role-based workflow.

---

## 2. Target Audience & Roles

### 2.1 Placement Officer (Admin)
- **Goal**: Oversee campus recruitment, onboard corporate partners, create drives with eligibility criteria, and track placement statistics.
- **Permissions**: Full access to companies, drives, student master list, applications, and placement metrics.

### 2.2 Student
- **Goal**: Maintain academic profile, discover matching placement drives, run automated eligibility checks, apply to drives, track interview schedules, and respond to employment offers.
- **Permissions**: Profile edit access, drive discovery (read-only), application submission, interview view, offer response.

### 2.3 Recruiter
- **Goal**: Evaluate applicants for company-specific placement drives, shortlist candidates, schedule interviews, grade interview outcomes, select final candidates, and generate official offer letters.
- **Permissions**: Access scoped strictly to candidates who applied to their company's placement drives.

---

## 3. Core Functional Requirements

| Module | ID | Requirement Description | Actor |
| :--- | :--- | :--- | :--- |
| **Auth** | FR-01 | Register as Student with email verification / password security. | Student |
| **Auth** | FR-02 | Secure JWT-based authentication with role claims. | All Roles |
| **Profile** | FR-03 | Maintain Personal, Academic (Branch, CGPA, Backlogs), and Skill profiles. | Student |
| **Profile** | FR-04 | Profile completeness check locking drive applications until 100% filled. | Backend |
| **Company** | FR-05 | Create, update, activate/deactivate corporate entities and recruiter mappings. | Admin |
| **Drives** | FR-06 | Create placement drives with explicit eligibility constraints and deadlines. | Admin |
| **Eligibility** | FR-07 | Automated backend engine evaluating student metrics against drive criteria. | Backend Engine |
| **Applications** | FR-08 | Apply to open drives with duplicate prevention and eligibility enforcement. | Student |
| **Shortlisting**| FR-09 | Filter applicants by CGPA/Branch and update status (Shortlist / Reject). | Recruiter |
| **Interviews** | FR-10 | Schedule interviews for shortlisted candidates and record feedback/results. | Recruiter |
| **Selection** | FR-11 | State machine transition enforcement (`PASSED` -> `SELECTED`). | Recruiter / Backend |
| **Offers** | FR-12 | Generate formal employment offers and allow student Accept/Decline. | Recruiter / Student |
| **Dashboard** | FR-13 | Role-specific dashboards showcasing KPIs, active drives, and application stats.| All Roles |
| **Alerts** | FR-14 | Real-time in-app notification pipeline for status updates. | Backend |

---

## 4. Technical & Non-Functional Requirements
- **Security**: Password hashing using `bcrypt`, JWT signature with HMAC-SHA256, RBAC Middleware.
- **Database**: SQLite database initialized with clean migration paths for PostgreSQL (SQLAlchemy ORM).
- **Backend**: Python 3.10+, FastAPI framework with Pydantic validation models.
- **Frontend**: React 18, Vite, Tailwind CSS, Axios HTTP Client, React Router v6.
- **Performance**: Eligibility check response time under 100ms for 1,000+ drives.
