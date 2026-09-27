# 10–15 Minute Assessment Demo Script

## 1. Demo Flow Sequence

### Step 1: Admin Dashboard & Onboarding (2 Mins)
1. Log in as Placement Officer (`admin@placement.edu`).
2. Show Admin Dashboard with live stats (Total Students, Active Companies, Open Drives, Placement %).
3. Add a new hiring partner: **Thinqloud Systems** (Location: Pune, Industry: IT Services).
4. Register a recruiter account mapped to Thinqloud Systems (`recruiter@thinqloud.com`).

### Step 2: Placement Drive Creation (2 Mins)
1. Navigate to **Placement Drives** -> Click **Create Drive**.
2. Fill details:
   - Role: *Software Engineer — AIML*
   - Package: *₹8.5 LPA*
   - Min CGPA: *7.5*
   - Allowed Branches: *CSE, AIML, IT*
   - Max Backlogs: *0*
   - Required Skills: *Python, SQL*
   - Application Deadline: *Future Date*
3. Show that Drive status is computed as `OPEN`.

### Step 3: Student Login, Profile Completion & Eligibility Check (3 Mins)
1. Log in as Student (`student@college.edu`).
2. Show complete student profile: CGPA `7.8`, Branch `AIML`, Backlogs `0`, Skills `Python, SQL, React`.
3. Open **Drive Discovery** page -> Select **Thinqloud Systems** Drive.
4. Highlight **Automated Eligibility Engine Result**: System displays `ELIGIBLE` with green checkmarks for all criteria.
5. Demonstrate edge case: Temporarily change CGPA to `7.0` -> System instantly returns `NOT ELIGIBLE` with exact reason: *"Required CGPA: 7.5, Current CGPA: 7.0"*. Revert CGPA to `7.8`.
6. Click **Apply Now** -> Application state created as `APPLIED`.

### Step 4: Recruiter Shortlisting & Interview (3 Mins)
1. Log in as Recruiter (`recruiter@thinqloud.com`).
2. Open Recruiter Dashboard -> View drive applicants.
3. Review candidate's academic stats and skills.
4. Click **Shortlist** -> Status updates to `SHORTLISTED`.
5. Click **Schedule Interview** -> Set Date/Time, Mode (*Online*), Meeting Link (*Google Meet link*).
6. Candidate receives in-app notification.
7. Post-interview, Recruiter opens interview feedback modal -> Select Result `PASSED` -> Submit feedback.

### Step 5: Selection & Formal Offer Generation (2 Mins)
1. Recruiter updates applicant state to `SELECTED` (State machine verifies passed interview).
2. Click **Generate Offer Letter**: Fill CTC *₹8.5 LPA*, Joining Date, Offer Date.
3. Status updates to `OFFERED`.

### Step 6: Student Offer Acceptance & Final Placement Statistics (2 Mins)
1. Log back in as Student.
2. View **My Offers** -> See formal Offer Letter from Thinqloud Systems.
3. Click **Accept Offer** -> Status updates to `ACCEPTED`.
4. Log back in as Admin -> Show updated Placement Stats & Charts.
