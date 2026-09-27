# Business Workflow & Lifecycle Architecture

## 1. Complete End-to-End Workflow Diagram

```text
       PLACEMENT OFFICER                             STUDENT                             RECRUITER
  +--------------------------+             +--------------------------+             +--------------------------+
  |  1. Onboard Company &    |             |  4. Register & Complete  |             |                          |
  |     Recruiter Account    |             |     Academic Profile     |             |                          |
  +--------------------------+             +--------------------------+             +--------------------------+
                |                                        |                                        |
                v                                        v                                        |
  +--------------------------+             +--------------------------+                           |
  |  2. Create Placement     |             |  5. Browse Open Drives & |                           |
  |     Drive Criteria       |             |     Check Eligibility    |                           |
  +--------------------------+             +--------------------------+                           |
                |                                        |                                        |
                +-------------------. .------------------+                                        |
                                     |                                                            |
                                     v                                                            v
                           +-------------------+                                    +--------------------------+
                           | 6. Backend Runs   |                                    | 7. Review Applicants &   |
                           |    Eligibility    |----------------------------------->|    Shortlist Candidates  |
                           |    Rule Verification|                                  +--------------------------+
                           +-------------------+                                                 |
                                     |                                                           v
                                     v                                              +--------------------------+
                           +-------------------+                                    | 8. Schedule Interview    |
                           |  Student Applies  |                                    |    (Online/Offline)      |
                           +-------------------+                                    +--------------------------+
                                                                                                 |
                                                                                                 v
                                                                                    +--------------------------+
                                                                                    | 9. Submit Interview      |
                                                                                    |    Result (Passed/Failed)|
                                                                                    +--------------------------+
                                                                                                 |
                                                                                                 v
  +--------------------------+             +--------------------------+             +--------------------------+
  | 12. View Placement Stats |<------------| 11. View & Accept/Decline|<------------| 10. Mark Candidate       |
  |     & Final Metrics      |             |     Formal Offer Letter  |             |     SELECTED & Issue Offer|
  +--------------------------+             +--------------------------+             +--------------------------+
```

---

## 2. Phase-by-Phase Process Explanation

### Step 1: Onboarding (Placement Officer)
- Admin creates a company profile (e.g., *Thinqloud Systems*) and registers a Recruiter login associated with that company.

### Step 2: Drive Creation & Criteria Definition
- Admin sets up a placement drive specifying: Job Title, CTC Package, Minimum CGPA, Allowed Branches, Max Backlogs, Target Graduation Year, Required Skills, and Application Deadline.

### Step 3: Student Registration & Profile Completion
- Student creates an account and fills academic metrics (Branch: `AIML`, CGPA: `7.8`, Backlogs: `0`, Graduation: `2027`, Skills: `Python, SQL`).
- System prevents application until all mandatory profile fields are non-null.

### Step 4: Eligibility Check & Application
- Student navigates to the drive details page.
- The **Backend Eligibility Engine** evaluates student stats against drive parameters in real time.
- If eligible, the "Apply Now" button unlocks. Upon submission, an application record with status `APPLIED` is created.

### Step 5: Recruiter Review & Shortlisting
- The recruiter logs into their dashboard, sees all candidates who applied to their drives, filters candidates by CGPA/Branch, and transitions selected candidates to `SHORTLISTED` (or `REJECTED`).

### Step 6: Interview Scheduling & Result Evaluation
- For candidates marked `SHORTLISTED`, the recruiter schedules an interview round with date, time, mode, and meeting link.
- Following the interview, the recruiter logs feedback and sets the interview result to `PASSED` or `FAILED`.

### Step 7: Selection & Formal Offer Generation
- If candidate's interview result is `PASSED`, the recruiter updates the application status to `SELECTED`.
- Recruiter generates an Offer Letter specifying CTC Package, Offer Date, and Joining Date.

### Step 8: Offer Acceptance & Placement Officer Overview
- Student receives an in-app notification, views the formal offer letter in their portal, and marks it as `ACCEPTED` or `DECLINED`.
- Admin dashboard updates overall campus placement percentage statistics.
