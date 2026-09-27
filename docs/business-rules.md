# Business Rules & Validation Matrix

## 1. Core System Business Rules

### BR-01: Profile Completeness Requirement
A student MUST have a fully populated profile before evaluating drive eligibility or applying.
- Required fields: `student_code`, `phone`, `branch`, `graduation_year`, `cgpa`, `backlogs`, and at least 1 `skill`.

### BR-02: Backend Eligibility Engine Standard
Frontend UI checks are purely for UX. All eligibility checks must be re-run on backend during POST `/applications`.
- **Criteria evaluated**:
  1. `student.cgpa >= drive.min_cgpa`
  2. `student.branch IN drive.allowed_branches`
  3. `student.graduation_year == drive.graduation_year`
  4. `student.backlogs <= drive.max_backlogs`
  5. `drive.required_skills SUBSET_OF student.skills`

### BR-03: Duplicate Application Prevention
A student can apply to a specific placement drive **exactly once**. Database unique constraint `UNIQUE(student_id, drive_id)` enforces this at DB level.

### BR-04: Deadline Strictness
System rejects application attempts if `current_timestamp > drive.application_deadline` or drive status is `CLOSED`.

### BR-05: Recruiter Data Isolation
Recruiters are scoped to their mapped company (`recruiter.company_id`). They cannot view or manage applicants of another company's drives.

### BR-06: Interview Prerequisites
Interviews can ONLY be scheduled for applications with status `SHORTLISTED`.

### BR-07: Selection State Machine Integrity
A candidate can transition to `SELECTED` status ONLY if:
1. Application status is currently `INTERVIEW` (or `SHORTLISTED`).
2. There exists an associated interview record with `result == 'PASSED'`.
3. If interview result is `FAILED`, status MUST be set to `REJECTED`. Direct transition from `FAILED` to `SELECTED` is strictly forbidden.

### BR-08: Offer Generation Constraint
An offer letter can ONLY be generated for candidates whose application status is `SELECTED`.

---

## 2. Application State Transition Diagram

```text
               +---------------+
               |    APPLIED    |
               +---------------+
                 /           \
                /             \ (Recruiter Reject)
               v               v
       +---------------+   +---------------+
       |  SHORTLISTED  |   |   REJECTED    |
       +---------------+   +---------------+
               |                   ^
               v                   |
       +---------------+           |
       |   INTERVIEW   |           |
       +---------------+           |
         /           \             |
 (Passed)           (Failed)       |
       v               v           |
+---------------+   +--------------+
|   SELECTED    |-->|   REJECTED   |
+---------------+   +--------------+
       |
       v
+---------------+
| OFFER CREATED |
+---------------+
```
