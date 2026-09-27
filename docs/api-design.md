# API Interface Specifications

## 1. Overview
All REST APIs adhere to standardized JSON payloads, standard HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`), and JWT Bearer token authentication in header: `Authorization: Bearer <token>`.

---

## 2. Authentication API (`/auth`)
- `POST /auth/register` — Student registration. Body: `{ email, password, full_name, student_code, branch, graduation_year, cgpa, backlogs }`. Returns `201 Created`.
- `POST /auth/login` — OAuth2 Form data (`username`, `password`). Returns `{ access_token, token_type, role, user_id, email, full_name }`.
- `GET /auth/me` — Returns current logged-in user context.

---

## 3. Student Profile API (`/students`)
- `GET /students/me` — Fetch detailed profile of logged-in student including skills.
- `PUT /students/me` — Update academic/personal info (`phone`, `branch`, `graduation_year`, `cgpa`, `backlogs`).
- `POST /students/me/skills` — Add skill to student profile. Body: `{ skill_name }`.
- `DELETE /students/me/skills/{skill_id}` — Remove skill from student profile.

---

## 4. Company API (`/companies`)
- `POST /companies` — [Admin] Create company profile & optional recruiter assignment.
- `GET /companies` — Fetch active companies list.
- `GET /companies/{id}` — Fetch detailed company profile.
- `PUT /companies/{id}` — [Admin] Update company details or toggle `is_active`.

---

## 5. Placement Drive API (`/drives`)
- `POST /drives` — [Admin] Create placement drive with eligibility rules & deadlines.
- `GET /drives` — Fetch placement drives (Supports query filters: `status`, `company_id`).
- `GET /drives/{id}` — Fetch drive details.
- `PUT /drives/{id}` — [Admin] Update placement drive parameters.

---

## 6. Eligibility Engine API (`/drives/{id}/eligibility`)
- `GET /drives/{id}/eligibility` — Runs backend eligibility logic comparing logged-in student profile against drive parameters.
  - Returns:
  ```json
  {
    "is_eligible": false,
    "is_profile_complete": true,
    "reasons": [
      "Minimum required CGPA is 8.0, but your CGPA is 7.6",
      "Drive allows branches [CSE, IT], but your branch is AIML"
    ]
  }
  ```

---

## 7. Application API (`/applications`)
- `POST /applications` — [Student] Apply for placement drive. Validates profile completeness, drive status, backend eligibility, and duplicate submissions.
- `GET /applications` — Fetch applications (Students see their applications; Recruiters see applicants for their company drives; Admins see all).
- `GET /applications/{id}` — Detailed application view with interview history & offer details.
- `PUT /applications/{id}/status` — [Recruiter/Admin] Transition application status (`SHORTLISTED`, `REJECTED`).

---

## 8. Interview API (`/interviews`)
- `POST /interviews` — [Recruiter] Schedule interview for a shortlisted application.
- `GET /interviews` — View scheduled interviews.
- `PUT /interviews/{id}` — [Recruiter] Log feedback and update interview result (`PASSED` or `FAILED`).

---

## 9. Offer API (`/offers`)
- `POST /offers` — [Recruiter] Generate job offer for candidate with application status `SELECTED`.
- `GET /offers` — View offers.
- `PUT /offers/{id}/status` — [Student] Accept or decline job offer (`ACCEPTED` or `DECLINED`).

---

## 10. Dashboard & Notifications API (`/dashboards`, `/notifications`)
- `GET /dashboards/stats` — Metrics endpoint returning role-based summary KPIs.
- `GET /notifications` — Fetch user notification feed.
- `PUT /notifications/{id}/read` — Mark notification as read.
