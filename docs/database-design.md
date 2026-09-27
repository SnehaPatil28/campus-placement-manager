# Database Design & ER Diagram

## 1. Relational Entity Explanation

| Entity Table | Primary Key | Key Foreign Keys | Purpose & Business Context |
| :--- | :--- | :--- | :--- |
| **`users`** | `id` | None | Base identity store for authentication (Admin, Student, Recruiter). |
| **`students`** | `id` | `user_id` -> `users.id` | Academic and personal profile store for student role. |
| **`skills`** | `id` | None | Normalized dictionary of technical skills (e.g., Python, SQL, React). |
| **`student_skills`** | `(student_id, skill_id)` | FKs to `students`, `skills` | Many-to-many join table for student skill sets. |
| **`companies`** | `id` | None | Onboarded corporate hiring partners. |
| **`recruiters`** | `id` | `user_id` -> `users`, `company_id` -> `companies` | Links recruiter user accounts to their respective company profile. |
| **`placement_drives`** | `id` | `company_id` -> `companies`, `created_by` -> `users` | Hiring job postings containing eligibility criteria & deadlines. |
| **`drive_skills`** | `(drive_id, skill_id)` | FKs to `placement_drives`, `skills` | Mandatory skill requirements for placement drives. |
| **`applications`** | `id` | `drive_id` -> `placement_drives`, `student_id` -> `students` | Core candidate job application lifecycle tracking entity. |
| **`interviews`** | `id` | `application_id` -> `applications.id` | Schedules, meeting details, and outcome records for interviews. |
| **`offers`** | `id` | `application_id` -> `applications.id` | Official employment offers generated for selected candidates. |
| **`notifications`** | `id` | `user_id` -> `users.id` | In-app user notifications for status updates and reminders. |

---

## 2. Entity-Relationship (ER) Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o| STUDENTS : "is profile of"
    USERS ||--o| RECRUITERS : "belongs to account"
    COMPANIES ||--o{ RECRUITERS : "employs"
    COMPANIES ||--o{ PLACEMENT_DRIVES : "hosts"
    
    STUDENTS ||--o{ STUDENT_SKILLS : "possesses"
    SKILLS ||--o{ STUDENT_SKILLS : "classified in"
    
    PLACEMENT_DRIVES ||--o{ DRIVE_SKILLS : "requires"
    SKILLS ||--o{ DRIVE_SKILLS : "needed for"
    
    STUDENTS ||--o{ APPLICATIONS : "submits"
    PLACEMENT_DRIVES ||--o{ APPLICATIONS : "receives"
    
    APPLICATIONS ||--o{ INTERVIEWS : "has round"
    APPLICATIONS ||--o| OFFERS : "results in"
    
    USERS ||--o{ NOTIFICATIONS : "receives"

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role "ADMIN | STUDENT | RECRUITER"
        datetime created_at
    }

    STUDENTS {
        int id PK
        int user_id FK
        string student_code UK
        string phone
        string branch
        int graduation_year
        float cgpa
        int backlogs
        boolean is_profile_complete
    }

    COMPANIES {
        int id PK
        string name
        string industry
        string location
        string website
        boolean is_active
        datetime created_at
    }

    RECRUITERS {
        int id PK
        int user_id FK
        int company_id FK
    }

    PLACEMENT_DRIVES {
        int id PK
        int company_id FK
        string title
        string description
        float package_lpa
        string location
        float min_cgpa
        string allowed_branches "JSON Array"
        int graduation_year
        int max_backlogs
        datetime application_deadline
        string status "UPCOMING | OPEN | CLOSED"
        int created_by FK
        datetime created_at
    }

    SKILLS {
        int id PK
        string name UK
    }

    APPLICATIONS {
        int id PK
        int drive_id FK
        int student_id FK
        string status "APPLIED | SHORTLISTED | INTERVIEW | SELECTED | REJECTED"
        datetime applied_at
        datetime updated_at
    }

    INTERVIEWS {
        int id PK
        int application_id FK
        datetime scheduled_date
        string mode "ONLINE | OFFLINE"
        string location_or_link
        string round_name
        string feedback
        string result "PENDING | PASSED | FAILED"
        datetime created_at
    }

    OFFERS {
        int id PK
        int application_id FK
        float package_offered
        datetime joining_date
        datetime offer_date
        string status "OFFERED | ACCEPTED | DECLINED"
        datetime created_at
    }

    NOTIFICATIONS {
        int id PK
        int user_id FK
        string title
        string message
        boolean is_read
        datetime created_at
    }
```
